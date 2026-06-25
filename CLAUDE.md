# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack AI-powered insurance claims management dashboard.

- **Backend**: Python Flask + SQLite, runs on port 5000
- **Frontend**: React 18 (create-react-app), runs on port 3000
- **AI Agent**: Anthropic Claude (`claude-opus-4-7`) with tool use for the chat agent
- **External integration**: ServiceNow REST API (optional — developer instance may hibernate)

---

## Commands

### Backend
```powershell
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```powershell
cd frontend
npm install
npm start        # dev server at http://localhost:3000
npm run build    # production build → frontend/build/
npm test         # run React test suite
```

---

## Architecture

### Request flow
Browser → React (`localhost:3000`) → Flask API (`localhost:5000`) → SQLite (`backend/claims.db`)

The frontend never touches the DB directly. All state lives in the DB; the frontend fetches on mount and after every action.

### Backend (`backend/`)
| File | Role |
|---|---|
| `app.py` | Flask entry point — all routes, `threading.Timer` for reprocessing |
| `database.py` | `get_connection()`, `create_tables()` — called once on startup |
| `db_operations.py` | All DB reads/writes — import these instead of writing raw SQL in routes |
| `config.py` | Loads `.env` via `python-dotenv` |
| `servicenow_client.py` | ServiceNow REST client; `_check_hibernating()` detects HTML responses |
| `agents/claim_reprocessing_agent.py` | Claude agent with 4 tools, prompt caching, keyword fallback |

Startup sequence in `app.py`: `create_tables()` → `seed_claims()` → `migrate_statuses()` → register routes.

### Frontend (`frontend/src/`)
| File | Role |
|---|---|
| `App.js` | Root layout, tab nav, floating chat panel state |
| `components/Dashboard.js` | Stat cards, SVG donut chart, claims table, audit timeline, CSV export |
| `components/Chat.js` | Chat UI — renders bot messages via `react-markdown` |
| `components/IncidentLookup.js` | ServiceNow incident search with pagination and date filter |
| `components/Toast.js` + `hooks/useToast.js` | Toast notification system (slide-in, 4 types, auto-dismiss) |

Key frontend dependencies: `axios`, `react-icons`, `react-markdown`, `framer-motion`.

---

## Database

Four tables created by `create_tables()`: `claim`, `incidents`, `ai_analysis`, `audit_logs`.

### Claim statuses
| Status | Meaning |
|---|---|
| `Processing` | Awaiting review — reprocess button shown |
| `Reprocessing` | Transient — set immediately when reprocess starts, auto-clears after 10s |
| `Approved` | Completed (set by the 10s timer after reprocessing) |
| `Rejected` | Denied |
| `Processed` | Set only by the fake-reprocess endpoint (`/api/claims/<id>/fake-reprocess`) |

`migrate_statuses()` runs on every startup to normalize legacy values (`Pending` → `Processing`, `Processed` → `Approved`). The fake-reprocess endpoint sets `Processed` at runtime, so it is never normalized unless the server restarts.

`seed_claims()` uses `INSERT OR IGNORE` — idempotent, safe to call every startup. 12 sample claims seeded across Processing/Approved/Rejected.

---

## Reprocessing Flow

**Dashboard button path:**
1. `POST /api/claims/<id>/reprocess` — validates `status == 'Processing'`, sets `Reprocessing`
2. `threading.Timer(10.0)` fires `_complete_reprocessing()` → sets `Approved`
3. Frontend auto-refreshes at 11s, shows toast "Claim X approved successfully"

**Fake external API path:**
- `POST /api/claims/<id>/fake-reprocess` — instantly sets `status = 'Processed'`, `notes = 'Processed by agent'`, no timer

**Chat agent path:**
- Same 10s timer logic as dashboard, enforced inside `_execute_tool('reprocess_claim', ...)`

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/claims` | All claims |
| GET | `/api/dashboard/stats` | Stat cards + 3-slice chart data |
| GET | `/api/audit-logs` | Recent activity (last 50) |
| POST | `/api/claims/<id>/reprocess` | Reprocess — 10s timer → Approved |
| POST | `/api/claims/<id>/fake-reprocess` | Instantly sets Processed + notes |
| POST | `/api/chat` | Chat with AI agent |
| GET | `/api/incidents/analysis` | Full ServiceNow analysis |
| GET | `/api/incidents/<number>` | Single incident |
| POST | `/api/incidents/search` | Search incidents |

---

## AI Chat Agent

- Model: `claude-opus-4-7`, max 10 tool-call rounds per message
- System prompt uses `cache_control: ephemeral` (prompt caching)
- Keeps last 20 messages of history; skips consecutive same-role messages before sending to API
- Falls back to `_process_with_keywords()` when `ANTHROPIC_API_KEY` is absent
- Both paths enforce `status == 'Processing'` before allowing reprocess

---

## Conventions

- All status comparisons use exact string match (`== 'Processing'`, not `.lower()`)
- Frontend API base URL hardcoded as `http://localhost:5000` in `Dashboard.js` and `Chat.js`
- `INSERT OR IGNORE` for all seed data (idempotent)
- ServiceNow developer instance (`dev305020`) hibernates when idle — wake at developer.servicenow.com

---

## Environment Variables (`backend/.env`)

```
ANTHROPIC_API_KEY=sk-ant-...
SERVICENOW_INSTANCE=dev305020.service-now.com
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password
FLASK_ENV=development
PORT=5000
```
