import os
import requests as http
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DB_FILE     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claims.db")
SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claim_schema.sql")


def _turso_creds():
    from config import TURSO_DATABASE_URL, TURSO_AUTH_TOKEN
    return TURSO_DATABASE_URL, TURSO_AUTH_TOKEN


# ── Turso HTTP API helpers ─────────────────────────────────────────────────

def _turso_arg(v):
    """Convert a Python value to a Turso HTTP API typed argument."""
    if v is None:
        return {"type": "null"}
    if isinstance(v, bool):
        return {"type": "integer", "value": 1 if v else 0}
    if isinstance(v, int):
        return {"type": "integer", "value": v}
    if isinstance(v, float):
        return {"type": "float", "value": v}
    return {"type": "text", "value": str(v)}


def _decode_cell(cell):
    """Convert a Turso response cell to a Python value."""
    if cell is None or (isinstance(cell, dict) and cell.get("type") == "null"):
        return None
    if isinstance(cell, dict):
        t, v = cell.get("type", "text"), cell.get("value")
        if t == "integer":
            return int(v) if v is not None else None
        if t == "float":
            return float(v) if v is not None else None
        return v
    return cell


# ── Row wrapper ────────────────────────────────────────────────────────────

class _Row:
    """Behaves like sqlite3.Row — supports dict(row) and row['col']."""
    def __init__(self, columns, values):
        self._d = dict(zip(columns, values))

    def __getitem__(self, key):
        return self._d[key]

    def keys(self):
        return self._d.keys()

    def get(self, key, default=None):
        return self._d.get(key, default)

    def __iter__(self):
        return iter(self._d)


# ── Turso connection & cursor ──────────────────────────────────────────────

class _TursoCursor:
    def __init__(self, conn):
        self._conn = conn
        self._cols = []
        self._rows = []

    @property
    def description(self):
        if not self._cols:
            return None
        return [(c, None, None, None, None, None, None) for c in self._cols]

    def execute(self, sql, params=None):
        stmt = {"sql": sql}
        if params:
            stmt["args"] = [_turso_arg(p) for p in params]
        results = self._conn._pipeline([stmt])
        if results:
            r = results[0]
            self._cols = [c["name"] for c in r.get("cols", [])]
            self._rows = [[_decode_cell(cell) for cell in row] for row in r.get("rows", [])]
        return self

    def executemany(self, sql, params_list):
        stmts = []
        for params in params_list:
            stmt = {"sql": sql}
            if params:
                stmt["args"] = [_turso_arg(p) for p in params]
            stmts.append(stmt)
        if stmts:
            self._conn._pipeline(stmts)
        self._cols, self._rows = [], []
        return self

    def fetchone(self):
        if not self._rows:
            return None
        return _Row(self._cols, self._rows[0])

    def fetchall(self):
        return [_Row(self._cols, r) for r in self._rows]


class _TursoConn:
    def __init__(self, base_url, token):
        # Accept libsql:// or https:// format
        self._url = base_url.replace("libsql://", "https://", 1).rstrip("/")
        self._token = token

    def _pipeline(self, stmts):
        """Send statements to Turso HTTP pipeline endpoint."""
        body = {"requests": [{"type": "execute", "stmt": s} for s in stmts] + [{"type": "close"}]}
        resp = http.post(
            f"{self._url}/v2/pipeline",
            headers={"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"},
            json=body,
            timeout=30,
            verify=False,  # corporate SSL inspection proxy uses a custom CA
        )
        resp.raise_for_status()
        results = []
        for item in resp.json().get("results", []):
            if item.get("type") == "error":
                raise Exception(item.get("error", {}).get("message", "Turso error"))
            if item.get("type") == "ok":
                r = item.get("response", {})
                if r.get("type") == "execute":
                    results.append(r.get("result", {}))
        return results

    def cursor(self):
        return _TursoCursor(self)

    def execute(self, sql, params=None):
        cur = _TursoCursor(self)
        cur.execute(sql, params)
        return cur

    def executemany(self, sql, params_list):
        cur = _TursoCursor(self)
        cur.executemany(sql, params_list)
        return cur

    def commit(self):
        pass  # each HTTP request is auto-committed

    def close(self):
        pass


# ── Public API ─────────────────────────────────────────────────────────────

def get_connection():
    url, token = _turso_creds()
    if url and token:
        return _TursoConn(url, token)
    # Fallback: local SQLite
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_number TEXT UNIQUE NOT NULL,
            title           TEXT NOT NULL,
            description     TEXT,
            priority        TEXT,
            category        TEXT,
            status          TEXT DEFAULT 'new',
            caller          TEXT,
            created_at      TEXT,
            fetched_at      TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_analysis (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_number      TEXT NOT NULL,
            ai_summary           TEXT,
            root_cause           TEXT,
            business_impact      TEXT,
            validated_priority   TEXT,
            team_to_assign       TEXT,
            recommended_action   TEXT,
            escalate             TEXT,
            created_at           TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claim (
            id           TEXT PRIMARY KEY,
            batch_id     TEXT UNIQUE NOT NULL,
            claim_number TEXT UNIQUE NOT NULL,
            member_id    TEXT UNIQUE NOT NULL,
            status       TEXT NOT NULL,
            amount       REAL NOT NULL,
            description  TEXT,
            created_date TEXT,
            last_updated TEXT,
            notes        TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            action          TEXT NOT NULL,
            tool            TEXT,
            status          TEXT,
            details         TEXT,
            incident_number TEXT,
            duration_ms     INTEGER,
            created_at      TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def init_db_from_schema(schema_path=SCHEMA_FILE):
    """Local SQLite only — skipped in Turso mode."""
    url, token = _turso_creds()
    if url and token:
        print("Turso mode: tables created via create_tables().")
        return
    import sqlite3
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        with open(schema_path, "r") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print(f"Database initialized from {schema_path}.")
    else:
        print("Database already exists.")


if __name__ == "__main__":
    create_tables()
    init_db_from_schema()
