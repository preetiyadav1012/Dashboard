from database import get_connection

# Save Incident
def save_incident(incident):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO incidents (
            incident_number, title, description,
            priority, category, status, caller, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        incident.get('number'),
        incident.get('short_description'),
        incident.get('description'),
        incident.get('priority'),
        incident.get('category'),
        incident.get('state', '1'),
        incident.get('caller_id', {}).get('display_value', 'Unknown'),
        incident.get('sys_created_on')
    ))
    conn.commit()
    conn.close()

# Save Claim
def save_claim(claim):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO claim (
            id, batch_id, claim_number, member_id,
            status, amount, description, created_date, last_updated, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            claim.get('id'),
            claim.get('batch_id'),
            claim.get('claim_number'),
            claim.get('member_id'),
            claim.get('status'),
            claim.get('amount'),
            claim.get('description'),
            claim.get('created_date'),
            claim.get('last_updated'),
            claim.get('notes'),
        )
    )
    conn.commit()
    conn.close()


def seed_claims():
    """Insert sample claims, skipping any that already exist by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    records = [
        ('1',  '123458901', 'ZX02FL1111', 'U123456782', 'UI Draft',     5000.00,  'Medical claim for surgery',        '2024-04-15', '2024-04-15T10:00:00', 'Awaiting submission'),
        ('2',  '856406962', 'ZX02FL2222', 'U123456783', 'UI Draft',     2500.00,  'Dental treatment claim',           '2024-04-20', '2024-04-20T11:00:00', 'Draft in progress'),
        ('3',  '111111111', 'ZX02FL3333', 'U123456784', 'EDI Complete', 1500.00,  'Vision care claim',                '2024-04-10', '2024-04-10T09:00:00', 'Submitted successfully'),
        ('4',  '223344556', 'ZX02FL4444', 'U123456785', 'UI Draft',     8750.00,  'Orthopedic surgery claim',         '2024-05-01', '2024-05-01T08:30:00', 'Missing lab reports'),
        ('5',  '334455667', 'ZX02FL5555', 'U123456786', 'UI Draft',     3200.00,  'Physiotherapy sessions claim',     '2024-05-03', '2024-05-03T14:00:00', 'Verification in progress'),
        ('6',  '445566778', 'ZX02FL6666', 'U123456787', 'EDI Complete', 6100.00,  'Hospitalization claim',            '2024-04-28', '2024-05-02T16:00:00', 'EDI submission successful'),
        ('7',  '556677889', 'ZX02FL7777', 'U123456788', 'EDI Complete', 950.00,   'Prescription drug claim',          '2024-04-22', '2024-04-22T10:00:00', 'Submitted and disbursed'),
        ('8',  '667788990', 'ZX02FL8888', 'U123456789', 'UI Draft',     12300.00, 'Cardiac procedure claim',          '2024-05-05', '2024-05-05T09:00:00', 'Missing critical documentation'),
        ('9',  '778899001', 'ZX02FL9999', 'U123456790', 'UI Draft',     4500.00,  'MRI and diagnostics claim',        '2024-05-04', '2024-05-04T11:30:00', 'Insurance verification pending'),
        ('10', '889900112', 'ZX02FL0000', 'U123456791', 'UI Draft',     2800.00,  'Emergency room visit claim',       '2024-04-18', '2024-04-30T15:00:00', 'Duplicate check in progress'),
        ('11', '990011223', 'ZX02FL1122', 'U123456792', 'EDI Processing', 7400.00,  'Maternity and newborn care claim', '2024-05-06', '2024-05-06T08:00:00', 'EDI batch submitted — awaiting response'),
        ('12', '001122334', 'ZX02FL2233', 'U123456793', 'UI Draft',     1850.00,  'Mental health counselling claim',  '2024-05-02', '2024-05-02T13:00:00', 'Coverage verification pending'),
        ('13', '112233445', 'ZX02FL3344', 'U123456794', 'UI Draft',     9200.00,  'Spinal cord injury claim',         '2024-05-07', '2024-05-07T09:00:00', 'Specialist review required'),
        ('14', '223344557', 'ZX02FL4455', 'U123456795', 'EDI Complete', 3750.00,  'Ambulance services claim',         '2024-05-08', '2024-05-08T10:30:00', 'Submitted and paid'),
        ('15', '334455668', 'ZX02FL5566', 'U123456796', 'UI Draft',     5600.00,  'Cosmetic surgery claim',           '2024-05-09', '2024-05-09T11:00:00', 'Policy review required'),
        ('16', '445566779', 'ZX02FL6677', 'U123456797', 'EDI Processing', 1100.00,  'Lab tests and blood work claim',   '2024-05-10', '2024-05-10T08:00:00', 'EDI submitted — awaiting payer'),
        ('17', '556677880', 'ZX02FL7788', 'U123456798', 'EDI Complete', 18500.00, 'Cancer treatment claim',           '2024-05-01', '2024-05-11T14:00:00', 'Submitted after oncology review'),
        ('18', '667788991', 'ZX02FL8899', 'U123456799', 'EDI Processing', 4300.00,  'Knee replacement surgery claim',   '2024-05-11', '2024-05-11T09:30:00', 'EDI transmission in progress'),
        ('19', '778899002', 'ZX02FL9900', 'U123456800', 'EDI Accepted', 720.00,   'Alternative medicine claim',       '2024-05-03', '2024-05-03T16:00:00', 'Adjusted and accepted'),
        ('20', '889900113', 'ZX02FL0011', 'U123456801', 'EDI Complete', 2200.00,  'Post-surgery rehabilitation claim','2024-05-06', '2024-05-12T10:00:00', 'Submitted for 6 sessions'),
        ('21', '990011224', 'ZX02FL1133', 'U123456802', 'EDI Processing', 6800.00,  'Diabetes management claim',        '2024-05-12', '2024-05-12T11:00:00', 'EDI processing — payer review pending'),
        ('22', '001122335', 'ZX02FL2244', 'U123456803', 'EDI Complete', 11200.00, 'Hip fracture surgery claim',       '2024-04-25', '2024-05-10T13:00:00', 'Fully submitted and disbursed'),
        ('23', '112233446', 'ZX02FL3355', 'U123456804', 'EDI Accepted', 3400.00,  'Experimental drug therapy claim',  '2024-05-08', '2024-05-08T15:00:00', 'Adjusted claim accepted'),
        ('24', '223344558', 'ZX02FL4466', 'U123456805', 'EDI Processing', 890.00,   'Allergy testing claim',            '2024-05-13', '2024-05-13T08:30:00', 'EDI queue — awaiting allergist confirmation'),
        ('25', '334455669', 'ZX02FL5577', 'U123456806', 'EDI Complete',   5300.00,  'Stroke rehabilitation claim',       '2024-05-05', '2024-05-13T09:00:00', 'Submitted — therapy sessions ongoing'),
        ('26', '445566780', 'ZX02FL6688', 'U123456807', 'EDI Processing', 7200.00,  'Liver transplant claim',            '2024-05-14', '2024-05-14T08:00:00', 'Submitted to EDI — awaiting clearance'),
        ('27', '556677891', 'ZX02FL7799', 'U123456808', 'EDI Processing', 3900.00,  'Physical therapy claim',            '2024-05-14', '2024-05-14T09:30:00', 'EDI batch submitted — pending response'),
        ('28', '667788902', 'ZX02FL8800', 'U123456809', 'EDI Processing', 15600.00, 'Cardiac bypass surgery claim',      '2024-05-15', '2024-05-15T10:00:00', 'High-value claim in EDI queue'),
        ('29', '778899013', 'ZX02FL9911', 'U123456810', 'EDI Processing', 2100.00,  'Dermatology treatment claim',       '2024-05-15', '2024-05-15T11:00:00', 'EDI processing — awaiting payer response'),
        ('30', '889900124', 'ZX02FL0022', 'U123456811', 'EDI Processing', 5850.00,  'Neonatal intensive care claim',     '2024-05-16', '2024-05-16T08:30:00', 'EDI transmission in progress'),
    ]
    cursor.executemany(
        """
        INSERT OR IGNORE INTO claim (
            id, batch_id, claim_number, member_id,
            status, amount, description, created_date, last_updated, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        records
    )
    conn.commit()
    conn.close()


def migrate_statuses():
    """Migrate legacy statuses to the 4-status system (UI Draft/EDI Processing/EDI Complete/EDI Accepted)."""
    conn = get_connection()
    conn.execute("UPDATE claim SET status='UI Draft'       WHERE status IN ('Pending', 'Processing')")
    conn.execute("UPDATE claim SET status='EDI Processing' WHERE status='Reprocessing'")
    conn.execute("UPDATE claim SET status='EDI Complete'   WHERE status='Approved'")
    conn.execute("UPDATE claim SET status='EDI Accepted'   WHERE status IN ('Processed', 'Rejected')")
    conn.commit()
    conn.close()


# Save AI Analysis
def save_ai_analysis(incident_number, analysis):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ai_analysis (
            incident_number, ai_summary,
            root_cause, business_impact,
            validated_priority, team_to_assign,
            escalate
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        incident_number,
        analysis.get('ai_summary'),
        analysis.get('root_cause'),
        analysis.get('business_impact'),
        analysis.get('validated_priority'),
        analysis.get('team_to_assign'),
        analysis.get('escalate')
    ))
    conn.commit()
    conn.close()

# Log Action (Audit Trail)
def log_action(action, tool, status,
               details=None, incident_number=None,
               duration_ms=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (
            action, tool, status,
            details, incident_number, duration_ms
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (action, tool, status,
          details, incident_number, duration_ms))
    conn.commit()
    conn.close()

# Get Summary Report
def get_summary_report():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM incidents')
    total_incidents = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM ai_analysis')
    total_analyses = cursor.fetchone()[0]
    cursor.execute(
        'SELECT COUNT(*) FROM ai_analysis WHERE escalate = ?',
        ['yes']
    )
    escalations = cursor.fetchone()[0]
    conn.close()
    return {
        'total_incidents': total_incidents,
        'total_analyses':  total_analyses,
        'escalations':     escalations,
    }

# Get All Incidents
def get_all_incidents():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM incidents ORDER BY fetched_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Get All Claims
def get_all_claims():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM claim")
    claims = cursor.fetchall()
    conn.close()
    return [dict(row) for row in claims]

def get_claim_by_id(claim_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM claim WHERE id = ? OR claim_number = ?",
        (claim_id, claim_id)
    )
    claim = cursor.fetchone()
    conn.close()
    return dict(claim) if claim else None


def update_claim_status_and_notes(claim_id, status, notes):
    conn = get_connection()
    conn.execute(
        "UPDATE claim SET status=?, notes=?, last_updated=datetime('now') WHERE id=?",
        (status, notes, claim_id)
    )
    conn.commit()
    conn.close()


# Get Audit Logs
def get_audit_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM audit_logs ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


