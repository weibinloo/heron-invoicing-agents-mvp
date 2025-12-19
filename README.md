# Invoice Automation MVP

## Overview
A minimal multi-agent demo that generates invoices from SQLite assignments. It uses LangChain to read the schema and draft the SQL query, then writes JSON + HTML invoices.

## Setup
1) Install dependencies:

```bash
pip install -r requirements.txt
```

2) Create your `.env` file from the template, then paste in your key:

```bash
cp .env.example .env
```

Open `.env` and set:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.1
```

Optional settings:
- `OPENAI_MODEL` (default: `gpt-5.1`)
- `INVOICE_DB_PATH` (default: `data/invoices.db`)
- `INVOICE_OUTPUT_DIR` (default: `invoices`)

## Run the demo
1) Seed demo data (creates `data/invoices.db` with a few completed assignments):

```bash
python scripts/seed_demo_data.py
```

2) Generate invoices for a month (this will call the LLM to build the SQL):

```bash
python -m app run --month 2025-11
```

3) See the effect
- Output files are written to `invoices/{client}/{YYYY-MM}/`.
- Example files after the run:
  - `invoices/C001/2025-11/invoice.json`
  - `invoices/C001/2025-11/invoice.html`
- Optional: inspect the SQLite database with `sqlite3 data/invoices.db`.

## Schema notes
The MVP includes the base tables in the prompt plus one optional override table:
- `client_assignment_overrides` for per-client credits or credit value overrides by assignment type.

The SQL agent will use this table if it exists; otherwise it will return `NULL` for override columns.

## What gets generated
Each invoice JSON contains line items, credits, and total amount; the HTML is a simple table view of the same data.
