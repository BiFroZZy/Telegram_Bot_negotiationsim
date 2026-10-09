"""Доменные модели — простые структуры данных без бизнес-логики."""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List, Dict


@dataclass
class Attempt:
    user_id: int
    username: str
    scenario_key: str
    scenario_title: str
    difficulty: str
    started_at: datetime
    score: Optional[int]
    review: str
    transcript: List[Dict[str, str]]


@dataclass
class Streak:
    user_id: int
    current_streak: int
    longest_streak: int
    last_active_date: Optional[date]
