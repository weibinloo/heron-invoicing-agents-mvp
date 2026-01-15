import os
import sqlite3
from datetime import datetime, timezone

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
        ("C003", "Blue Harbor PE", "finance@blueharbor.example", 9500, "USD"),
    ]
    conn.executemany(
        "INSERT INTO clients VALUES (?, ?, ?, ?, ?)",
        clients,
    )

    assignment_types = [
        ("Snapshot Assignment", 1.0),
        ("Network Build Assignment", 3.0),
        ("Portfolio Review Assignment", 2.0),
    ]
    conn.executemany(
        "INSERT INTO assignment_types VALUES (?, ?)",
        assignment_types,
    )

    assignments = [
        # 2025-09
        ("A9001", "C001", "Snapshot Assignment", "2025-09-03", "COMPLETED"),
        ("A9002", "C001", "Network Build Assignment", "2025-09-10", "COMPLETED"),
        ("A9003", "C002", "Snapshot Assignment", "2025-09-14", "COMPLETED"),
        ("A9004", "C002", "Portfolio Review Assignment", "2025-09-20", "COMPLETED"),
        ("A9005", "C003", "Network Build Assignment", "2025-09-22", "COMPLETED"),
        # 2025-10
        ("A1001", "C001", "Snapshot Assignment", "2025-10-05", "COMPLETED"),
        ("A1002", "C001", "Portfolio Review Assignment", "2025-10-18", "COMPLETED"),
        ("A1003", "C002", "Network Build Assignment", "2025-10-11", "COMPLETED"),
        ("A1004", "C002", "Snapshot Assignment", "2025-10-25", "COMPLETED"),
        ("A1005", "C003", "Portfolio Review Assignment", "2025-10-28", "COMPLETED"),
        # 2025-11
        ("A1101", "C001", "Snapshot Assignment", "2025-11-05", "COMPLETED"),
        ("A1102", "C001", "Network Build Assignment", "2025-11-18", "COMPLETED"),
        ("A1103", "C001", "Portfolio Review Assignment", "2025-11-22", "COMPLETED"),
        ("A1104", "C002", "Snapshot Assignment", "2025-11-02", "COMPLETED"),
        ("A1105", "C002", "Network Build Assignment", "2025-11-15", "COMPLETED"),
        ("A1106", "C002", "Portfolio Review Assignment", "2025-11-20", "COMPLETED"),
        ("A1107", "C003", "Snapshot Assignment", "2025-11-12", "COMPLETED"),
        ("A1108", "C003", "Network Build Assignment", "2025-11-26", "COMPLETED"),
        # Non-completed for noise
        ("A1109", "C003", "Snapshot Assignment", "2025-11-27", "IN_PROGRESS"),
    ]
    conn.executemany(
        "INSERT INTO assignments VALUES (?, ?, ?, ?, ?)",
        assignments,
    )

    overrides = [
        ("C001", "Snapshot Assignment", 1.5, None),
        ("C002", "Network Build Assignment", 2.5, 11000),
        ("C003", "Portfolio Review Assignment", 1.75, 9000),
    ]
    conn.executemany(
        "INSERT INTO client_assignment_overrides VALUES (?, ?, ?, ?)",
        overrides,
    )

    conn.commit()
    conn.close()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"Seeded data at {DB_PATH} ({now})")


if __name__ == "__main__":
    main()
