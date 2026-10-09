"""Подключение к PostgreSQL и применение миграций."""
import asyncpg
from pathlib import Path


async def create_pool(dsn: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=5)


async def run_migrations(pool: asyncpg.Pool, migrations_dir: Path) -> None:
    """Простое последовательное применение .sql файлов. Все запросы идемпотентны
    (IF NOT EXISTS), поэтому безопасно вызывать при каждом запуске бота."""
    files = sorted(migrations_dir.glob("*.sql"))
    async with pool.acquire() as con:
        for f in files:
            await con.execute(f.read_text(encoding="utf-8"))
