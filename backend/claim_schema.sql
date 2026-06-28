-- SQLite schema for claims table
CREATE TABLE IF NOT EXISTS claim (
    id TEXT PRIMARY KEY,
    batch_id TEXT UNIQUE NOT NULL,
    claim_number TEXT UNIQUE NOT NULL,
    member_id        TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    created_date TEXT,
    last_updated TEXT,
    notes TEXT
);

-- Example data
INSERT INTO claim (id, batch_id, claim_number, member_id, status, amount, description, created_date, last_updated, notes) VALUES
('1', '123458901', 'ZX02FL1111', 'U123456782', 'Pending', 5000.00, 'Medical claim for surgery', '2024-04-15', '2024-04-15T10:00:00', 'Awaiting documentation'),
('2', '856406962', 'ZX02FL2222', 'U123456783', 'Processing', 2500.00, 'Dental treatment claim', '2024-04-20', '2024-04-20T11:00:00', 'Under review'),
('3', '111111111', 'ZX02FL3333', 'U123456784', 'Approved', 1500.00, 'Vision care claim', '2024-04-10', '2024-04-10T09:00:00', 'Approved for payment');
