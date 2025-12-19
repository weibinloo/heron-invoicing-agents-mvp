import os

from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str
    db_path: str
    output_dir: str


def load_settings() -> Settings:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required")
    return Settings(
        openai_api_key=api_key,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.1").strip() or "gpt-5.1",
        db_path=os.getenv("INVOICE_DB_PATH", "data/invoices.db"),
        output_dir=os.getenv("INVOICE_OUTPUT_DIR", "invoices"),
    )
