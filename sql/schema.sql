PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    event_date TEXT NOT NULL,
    headline TEXT NOT NULL,
    source TEXT NOT NULL,
    description TEXT NOT NULL,
    url TEXT,
    source_type TEXT NOT NULL,
    collected_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS risk_analysis (
    event_id TEXT PRIMARY KEY,
    risk_category TEXT NOT NULL CHECK (risk_category IN (
        'Market Risk', 'Credit Risk', 'Operational Risk',
        'Technology Risk', 'Emerging Risk'
    )),
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    breadth INTEGER NOT NULL CHECK (breadth BETWEEN 1 AND 5),
    urgency INTEGER NOT NULL CHECK (urgency BETWEEN 1 AND 5),
    confidence INTEGER NOT NULL CHECK (confidence BETWEEN 1 AND 5),
    risk_score INTEGER NOT NULL CHECK (risk_score BETWEEN 20 AND 100),
    ai_summary TEXT NOT NULL,
    analyst_focus TEXT NOT NULL,
    analysis_method TEXT NOT NULL,
    analyzed_at TEXT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sectors (
    sector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS event_sectors (
    event_id TEXT NOT NULL,
    sector_id INTEGER NOT NULL,
    PRIMARY KEY (event_id, sector_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (sector_id) REFERENCES sectors(sector_id)
);

CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_risk_category ON risk_analysis(risk_category);
CREATE INDEX IF NOT EXISTS idx_risk_score ON risk_analysis(risk_score);

CREATE VIEW IF NOT EXISTS dashboard_events AS
SELECT
    e.event_id,
    e.event_date,
    e.headline,
    e.source,
    e.description,
    e.url,
    r.risk_category,
    r.severity,
    r.breadth,
    r.urgency,
    r.confidence,
    r.risk_score,
    r.ai_summary,
    r.analyst_focus,
    r.analysis_method,
    GROUP_CONCAT(s.sector_name, '; ') AS affected_sectors
FROM events e
JOIN risk_analysis r ON e.event_id = r.event_id
LEFT JOIN event_sectors es ON e.event_id = es.event_id
LEFT JOIN sectors s ON es.sector_id = s.sector_id
GROUP BY e.event_id;
