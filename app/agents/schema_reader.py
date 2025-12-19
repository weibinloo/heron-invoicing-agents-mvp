from __future__ import annotations

from dataclasses import dataclass

from langchain_community.utilities import SQLDatabase


@dataclass
class SchemaInfo:
    table_names: list[str]
    schema_text: str


class SchemaReaderAgent:
    def __init__(self, db_path: str) -> None:
        self._db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

    def read_schema(self) -> SchemaInfo:
        table_names = list(self._db.get_usable_table_names())
        schema_text = self._db.get_table_info(table_names)
        return SchemaInfo(table_names=table_names, schema_text=schema_text)
