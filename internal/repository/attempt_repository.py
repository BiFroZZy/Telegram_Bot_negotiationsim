"""Репозиторий истории попыток переговоров."""
import json
import asyncpg
from internal.domain.models import Attempt


class AttemptRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save(self, attempt: Attempt) -> None:
        await self.pool.execute(
            """INSERT INTO attempts
               (user_id, username, scenario_key, scenario_title, difficulty, started_at, score, review, transcript)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)""",
            attempt.user_id, attempt.username, attempt.scenario_key, attempt.scenario_title,
            attempt.difficulty, attempt.started_at, attempt.score, attempt.review,
            json.dumps(attempt.transcript, ensure_ascii=False),
        )

    async def get_history(self, user_id: int, limit: int = 8):
        return await self.pool.fetch(
            """SELECT scenario_title, difficulty, finished_at, score
               FROM attempts WHERE user_id=$1 ORDER BY id DESC LIMIT $2""",
            user_id, limit)

    async def get_scores(self, user_id: int) -> list:
        rows = await self.pool.fetch(
            "SELECT score FROM attempts WHERE user_id=$1 AND score IS NOT NULL ORDER BY id ASC",
            user_id)
        return [r["score"] for r in rows]
