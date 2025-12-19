import os
import sqlite3
from datetime import datetime

DB_PATH = os.getenv("INVOICE_DB_PATH", "data/invoices.db")


def main() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    conn.executescript(
        """
        DROP TABLE IF EXISTS clients;
        DROP TABLE IF EXISTS assignment_types;
        DROP TABLE IF EXISTS assignments;
        DROP TABLE IF EXISTS client_assignment_overrides;

        CREATE TABLE clients (
            client_id TEXT PRIMARY KEY,
            client_name TEXT,
            billing_email TEXT,
            default_credit_value_usd INTEGER,
            currency TEXT
        );

        CREATE TABLE assignment_types (
            assignment_type TEXT PRIMARY KEY,
            default_credits REAL
        );

        CREATE TABLE assignments (
            assignment_id TEXT PRIMARY KEY,
            client_id TEXT,
            assignment_type TEXT,
            completed_at TEXT,
            status TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(client_id),
            FOREIGN KEY (assignment_type) REFERENCES assignment_types(assignment_type)
        );

        CREATE TABLE client_assignment_overrides (
            client_id TEXT,
            assignment_type TEXT,
            credits_override REAL,
            credit_value_override_usd INTEGER,
            PRIMARY KEY (client_id, assignment_type),
            FOREIGN KEY (client_id) REFERENCES clients(client_id),
            FOREIGN KEY (assignment_type) REFERENCES assignment_types(assignment_type)
        );
        """
    )

    clients = [
        ("C001", "Redwood Capital", "billing@redwood.example", 10000, "USD"),
        ("C002", "Summit Partners", "ap@summit.example", 12000, "USD"),
    ]
    conn.executemany(
        "INSERT INTO clients VALUES (?, ?, ?, ?, ?)",
        clients,
    )

    assignment_types = [
        ("Snapshot Assignment", 1.0),
        ("Network Build Assignment", 3.0),
    ]
    conn.executemany(
        "INSERT INTO assignment_types VALUES (?, ?)",
        assignment_types,
    )

    assignments = [
        ("A1001", "C001", "Snapshot Assignment", "2025-11-05", "COMPLETED"),
        ("A1002", "C001", "Snapshot Assignment", "2025-11-18", "COMPLETED"),
        ("A1003", "C001", "Network Build Assignment", "2025-11-20", "COMPLETED"),
        ("A1004", "C001", "Network Build Assignment", "2025-10-12", "COMPLETED"),
        ("A2001", "C002", "Snapshot Assignment", "2025-11-02", "COMPLETED"),
        ("A2002", "C002", "Network Build Assignment", "2025-11-15", "COMPLETED"),
        ("A2003", "C002", "Network Build Assignment", "2025-11-20", "IN_PROGRESS"),
        ("A2004", "C002", "Snapshot Assignment", "2025-11-25", "COMPLETED"),
    ]
    conn.executemany(
        "INSERT INTO assignments VALUES (?, ?, ?, ?, ?)",
        assignments,
    )

    overrides = [
        ("C001", "Snapshot Assignment", 1.5, None),
        ("C002", "Network Build Assignment", 2.5, 11000),
    ]
    conn.executemany(
        "INSERT INTO client_assignment_overrides VALUES (?, ?, ?, ?)",
        overrides,
    )

    conn.commit()
    conn.close()
    print(f"Seeded demo data at {DB_PATH} ({datetime.utcnow().isoformat(timespec='seconds')}Z)")


if __name__ == "__main__":
    main()
