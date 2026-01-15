"""Generate a SQL query from the schema and a month window via LLM."""

from __future__ import annotations

import os
from dataclasses import dataclass

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict, Field


class SQLQueryOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sql: str = Field(..., description="A single SELECT statement with named parameters")
    notes: str = Field(..., description="Short reasoning")


@dataclass
class SQLQueryPlan:
    sql: str
    notes: str


class SQLWriterAgent:
    def __init__(self, model_name: str, api_key: str) -> None:
        self._parser = PydanticOutputParser(pydantic_object=SQLQueryOutput)
        self._llm = ChatOpenAI(model=model_name, api_key=api_key, temperature=0)

    def generate_query(
        self,
        schema_text: str,
        month_start: str,
        month_end: str,
        include_overrides: bool,
    ) -> SQLQueryPlan:
        template = """
You are a SQL analyst for SQLite. Use the schema to write a single SELECT statement.
Return JSON that matches the provided schema instructions.

Schema:
{schema_text}

Task:
- Select assignments with status = 'COMPLETED' and completed_at >= :month_start and < :month_end.
- Return one row per assignment (no aggregation).
- Always include these columns with exact aliases:
  assignment_id, client_id, client_name, billing_email, assignment_type,
  completed_at, status, default_credits, default_credit_value_usd, currency,
  credits_override, credit_value_override_usd.
- Join clients and assignment_types.
- If client_assignment_overrides exists, LEFT JOIN it on client_id + assignment_type and use its columns.
- If client_assignment_overrides does not exist, return NULL for credits_override and credit_value_override_usd.
- Only SELECT. No semicolons.

Format instructions:
{format_instructions}
"""
        prompt = ChatPromptTemplate.from_template(template)
        message = prompt.format(
            schema_text=schema_text,
            format_instructions=self._parser.get_format_instructions(),
        )
        response = self._llm.invoke(message)
        parsed = self._parser.parse(response.content)
        if os.getenv("SQL_DEBUG") == "1":
            print("LLM parsed.sql:\n" + parsed.sql)
        sql = self._normalize_sql(parsed.sql)
        if ":month_start" not in sql or ":month_end" not in sql:
            raise ValueError("SQL must use :month_start and :month_end parameters")
        if include_overrides and "client_assignment_overrides" not in sql:
            raise ValueError("SQL must reference client_assignment_overrides when available")
        return SQLQueryPlan(sql=sql, notes=parsed.notes)

    @staticmethod
    def _normalize_sql(sql: str) -> str:
        normalized = sql.strip()
        normalized = normalized.lstrip("\ufeff\u200b")
        if normalized.startswith("```"):
            normalized = normalized.strip("`")
        if normalized.lower().startswith("sql"):
            parts = normalized.split(None, 1)
            if len(parts) == 2:
                normalized = parts[1]
        lowered = normalized.lower()
        select_index = lowered.find("select ")
        with_index = lowered.find("with ")
        start_index = min(
            [idx for idx in [select_index, with_index] if idx != -1],
            default=0,
        )
        normalized = normalized[start_index:].strip()
        while normalized and not normalized[0].isalpha():
            normalized = normalized[1:].lstrip()
        return normalized.rstrip(";")
