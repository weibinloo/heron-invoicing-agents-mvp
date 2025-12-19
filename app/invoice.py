from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import load_settings
from app.db import connect
from app.models import AssignmentRow
from app.agents import InvoiceBuilderAgent, SchemaReaderAgent, SQLWriterAgent


@dataclass
class RunResult:
    invoices_written: int


def _month_bounds(month: str) -> tuple[str, str]:
    try:
        start = datetime.strptime(month, "%Y-%m")
    except ValueError as exc:
        raise ValueError("Month must be in YYYY-MM format") from exc
    year = start.year
    next_month = start.month + 1
    if next_month == 13:
        year += 1
        next_month = 1
    end = datetime(year, next_month, 1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _load_template() -> Environment:
    return Environment(
        loader=FileSystemLoader("app/templates"),
        autoescape=select_autoescape(["html"]),
    )


def run(month: str) -> RunResult:
    settings = load_settings()
    month_start, month_end = _month_bounds(month)

    conn = connect(settings.db_path)
    schema_agent = SchemaReaderAgent(settings.db_path)
    schema_info = schema_agent.read_schema()

    include_overrides = "client_assignment_overrides" in schema_info.table_names

    sql_agent = SQLWriterAgent(settings.openai_model, settings.openai_api_key)
    query_plan = sql_agent.generate_query(
        schema_text=schema_info.schema_text,
        month_start=month_start,
        month_end=month_end,
        include_overrides=include_overrides,
    )

    rows = conn.execute(
        query_plan.sql,
        {"month_start": month_start, "month_end": month_end},
    ).fetchall()

    assignments = [AssignmentRow(**dict(row)) for row in rows]

    if not assignments:
        return RunResult(invoices_written=0)

    builder = InvoiceBuilderAgent()
    packages = builder.build_invoices(assignments, month)

    env = _load_template()
    template = env.get_template("invoice.html")

    invoices_written = 0
    for package in packages:
        invoice = package.invoice

        output_dir = os.path.join(settings.output_dir, invoice.client_id, month)
        os.makedirs(output_dir, exist_ok=True)

        json_path = os.path.join(output_dir, "invoice.json")
        with open(json_path, "w", encoding="utf-8") as handle:
            handle.write(invoice.model_dump_json(indent=2))

        html_path = os.path.join(output_dir, "invoice.html")
        with open(html_path, "w", encoding="utf-8") as handle:
            handle.write(template.render(invoice=invoice))

        invoices_written += 1

    return RunResult(invoices_written=invoices_written)
