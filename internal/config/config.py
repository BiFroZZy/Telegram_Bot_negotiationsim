"""Загрузка конфигурации: .env (секреты) + configs/*.yaml (настройки без секретов)."""
import os
from dataclasses import dataclass, field
from pathlib import Path
import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


def _load_yaml(name: str) -> dict:
    path = ROOT_DIR / "configs" / name
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@dataclass
class Config:
    telegram_token: str
    gemini_api_key: str
    gemini_model: str
    database_url: str
    reminder_hour_utc: int
    difficulty: dict = field(default_factory=dict)
    reminder_messages: dict = field(default_factory=dict)


def load_config() -> Config:
    return Config(
        telegram_token=os.environ["TELEGRAM_TOKEN"],
        gemini_api_key=os.environ["GEMINI_API_KEY"],
        gemini_model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        database_url=os.environ["DATABASE_URL"],
        reminder_hour_utc=int(os.environ.get("REMINDER_HOUR_UTC", "17")),
        difficulty=_load_yaml("difficulty.yaml"),
        reminder_messages=_load_yaml("reminder.yaml"),
    )
