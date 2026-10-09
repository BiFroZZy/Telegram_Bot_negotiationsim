"""Репозиторий пользовательских данных: 'индекс доверия партнёров' (стрик)."""
import datetime
import asyncpg


class UserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_streak(self, user_id: int):
        return await self.pool.fetchrow(
            "SELECT current_streak, longest_streak, last_active_date FROM user_streaks WHERE user_id=$1",
            user_id)

    async def upsert_streak(self, user_id: int, current: int, longest: int, last_active: datetime.date) -> None:
        await self.pool.execute(
            """INSERT INTO user_streaks (user_id, current_streak, longest_streak, last_active_date)
               VALUES ($1,$2,$3,$4)
               ON CONFLICT (user_id) DO UPDATE
               SET current_streak=$2, longest_streak=$3, last_active_date=$4""",
            user_id, current, longest, last_active)

    async def all_streaks(self):
        return await self.pool.fetch(
            "SELECT user_id, current_streak, last_active_date FROM user_streaks")
