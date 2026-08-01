import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "expenses.json"


def _ensure_file() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_expenses() -> list[dict[str, Any]]:
    _ensure_file()
    try:
        text = DATA_FILE.read_text(encoding="utf-8").strip()
        if not text:
            return []
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error("expenses.json is corrupted — returning empty list")
        return []


def save_expenses(expenses: list[dict[str, Any]]) -> None:
    _ensure_file()
    DATA_FILE.write_text(
        json.dumps(expenses, indent=2, default=str),
        encoding="utf-8",
    )
