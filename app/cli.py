from __future__ import annotations

import argparse

from app.invoice import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate invoices for a billing month")
    parser.add_argument("run", nargs="?", help="run the invoice generator")
    parser.add_argument("--month", required=True, help="Billing month in YYYY-MM")
    args = parser.parse_args()

    result = run(args.month)
    print(f"Invoices written: {result.invoices_written}")
