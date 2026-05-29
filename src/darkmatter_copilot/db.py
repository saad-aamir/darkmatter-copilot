"""Database connection and schema management for Dark Matter Co-Pilot."""

import sqlite3
from contextlib import closing
from pathlib import Path

# Path to the database file (project_root/data/studio.db)
DB_PATH = Path(__file__).parent.parent.parent / "data" / "studio.db"


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS leads (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    company                 TEXT NOT NULL,
    contact_name            TEXT,
    contact_email           TEXT UNIQUE,
    contact_phone           TEXT,
    website_url             TEXT,
    source                  TEXT NOT NULL CHECK (source IN (
                                'referral', 'cold_outbound', 'inbound_form',
                                'linkedin', 'other'
                            )),
    source_detail           TEXT,
    existing_client_id      INTEGER REFERENCES clients(id),
    status                  TEXT NOT NULL DEFAULT 'new' CHECK (status IN (
                                'new', 'contacted', 'in_conversation',
                                'proposal_sent', 'won', 'lost', 'on_hold'
                            )),
    business_type           TEXT,
    notes                   TEXT,
    created_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_contact_at         TEXT
);

CREATE TABLE IF NOT EXISTS clients (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    name                    TEXT NOT NULL,
    contact_name            TEXT,
    contact_email           TEXT,
    contact_phone           TEXT,
    converted_from_lead_id  INTEGER REFERENCES leads(id),
    became_client_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes                   TEXT
);

CREATE TABLE IF NOT EXISTS projects (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id               INTEGER NOT NULL REFERENCES clients(id),
    name                    TEXT NOT NULL,
    project_type            TEXT NOT NULL CHECK (project_type IN (
                                'landing_page', 'saas_marketing', 'portfolio',
                                'ecommerce', 'redesign', 'corporate_site', 'other'
                            )),
    scope                   TEXT,
    price                   INTEGER,
    paid_at                 TEXT,
    started_at              TEXT,
    deadline                TEXT,
    completed_at            TEXT,
    status                  TEXT NOT NULL DEFAULT 'planning' CHECK (status IN (
                                'planning', 'in_progress', 'delivered',
                                'completed', 'on_hold', 'cancelled'
                            )),
    deployment_url          TEXT,
    notes                   TEXT,
    converted_from_lead_id  INTEGER REFERENCES leads(id),
    created_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS case_studies (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id              INTEGER NOT NULL UNIQUE REFERENCES projects(id),
    problem                 TEXT NOT NULL,
    approach                TEXT NOT NULL,
    result                  TEXT NOT NULL,
    tech_stack              TEXT,
    is_published            INTEGER NOT NULL DEFAULT 0,
    published_at            TEXT,
    created_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proposals (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id                 INTEGER NOT NULL REFERENCES leads(id),
    title                   TEXT NOT NULL,
    body                    TEXT NOT NULL,
    quoted_price            INTEGER,
    status                  TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
                                'pending', 'accepted', 'rejected'
                            )),
    sent_at                 TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    responded_at            TEXT,
    notes                   TEXT
);
"""


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with foreign keys enabled and Row factory set."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Create all tables if they don't already exist."""
    with closing(get_connection()) as conn:
        with conn:
            conn.executescript(SCHEMA_SQL)


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")