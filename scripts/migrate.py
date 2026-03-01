"""
Migration script for NexaFlow CRM.
Adds new columns and tables for all phases.
Safe to run multiple times — uses IF NOT EXISTS / try-except for columns.
"""
import sqlite3
import sys
import os

DB_PATH = os.getenv("DATABASE_PATH", "nexaflow.db")


def run_migration(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Helper: add column if not exists
    def add_column(table, column, col_type, default=None):
        try:
            default_clause = f" DEFAULT {default}" if default is not None else ""
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}{default_clause}")
            print(f"  Added {table}.{column}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"  {table}.{column} already exists, skipping")
            else:
                raise

    print("Phase 1: Contact-Project M2M + Budget")
    add_column("contacts", "notes", "TEXT", "''")
    add_column("projects", "budget", "REAL", "0.0")
    add_column("projects", "currency", "TEXT", "'USD'")
    add_column("projects", "actual_cost", "REAL", "0.0")
    add_column("projects", "start_date", "TEXT", "''")
    add_column("projects", "end_date", "TEXT", "''")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
            role TEXT DEFAULT 'team_member',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  project_contacts table ready")

    print("\nPhase 2: Multi-Currency")
    add_column("users", "preferred_currency", "TEXT", "'USD'")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rate_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_currency TEXT UNIQUE NOT NULL,
            rates_json TEXT NOT NULL,
            fetched_at DATETIME NOT NULL
        )
    """)
    print("  exchange_rate_cache table ready")

    print("\nPhase 3: Invoice Workflow + Communication Log")
    add_column("invoices", "currency", "TEXT", "'USD'")
    add_column("invoices", "invoice_number", "TEXT", "NULL")
    add_column("invoices", "title", "TEXT", "''")
    add_column("invoices", "notes", "TEXT", "''")
    add_column("invoices", "sent_at", "DATETIME", "NULL")
    add_column("invoices", "sent_to_email", "TEXT", "''")
    add_column("invoices", "opened_at", "DATETIME", "NULL")
    add_column("invoices", "tracking_token", "TEXT", "NULL")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoice_line_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
            description TEXT NOT NULL,
            quantity REAL DEFAULT 1.0,
            unit_price REAL DEFAULT 0.0,
            total REAL DEFAULT 0.0
        )
    """)
    print("  invoice_line_items table ready")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS communication_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            contact_id INTEGER REFERENCES contacts(id),
            project_id INTEGER REFERENCES projects(id),
            invoice_id INTEGER REFERENCES invoices(id),
            type TEXT NOT NULL,
            summary TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  communication_logs table ready")

    print("\nPhase 4: Milestones")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            due_date TEXT,
            completed_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  milestones table ready")

    conn.commit()
    conn.close()
    print("\nMigration complete!")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    print(f"Migrating database: {path}")
    run_migration(path)
