"""Бизнес-логика 'индекса доверия партнёров' (стрика по дням)."""
import datetime
from internal.repository.user_repository import UserRepository


class StreakService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_activity(self, user_id: int):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        row = await self.user_repo.get_streak(user_id)
        if row is None:
            current, longest = 1, 1
        else:
            current, longest = row["current_streak"], row["longest_streak"]
            last_active = row["last_active_date"]
            if last_active == today:
                return current, longest
            elif last_active == yesterday:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        await self.user_repo.upsert_streak(user_id, current, longest, today)
        return current, longest

    @staticmethod
    def trust_bar(n: int) -> str:
        n = max(0, min(n, 10))
        return "🟢" * n + "⚪" * (10 - n)

    @staticmethod
    def word_form(n: int) -> str:
        return "день" if n == 1 else "дня" if n < 5 else "дней"
