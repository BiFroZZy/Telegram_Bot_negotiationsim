"""Точка входа приложения.

Запуск из корня проекта:
    python -m cmd.app.main
"""
import datetime
from pathlib import Path
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from internal.config.config import load_config
from internal.repository.db import create_pool, run_migrations
from internal.repository.attempt_repository import AttemptRepository
from internal.repository.user_repository import UserRepository
from internal.service.gemini_service import GeminiService
from internal.service.streak_service import StreakService
from internal.service.negotiation_service import NegotiationService
from internal.bot import handlers
from internal.bot.jobs import daily_reminder

ROOT_DIR = Path(__file__).resolve().parents[2]


async def _bootstrap(app: Application, cfg) -> None:
    """Поднимаем пул к БД, применяем миграции, собираем сервисы и кладём их в bot_data."""
    pool = await create_pool(cfg.database_url)
    await run_migrations(pool, ROOT_DIR / "migrations")

    attempt_repo = AttemptRepository(pool)
    user_repo = UserRepository(pool)
    gemini = GeminiService(cfg.gemini_api_key, cfg.gemini_model)
    streak_service = StreakService(user_repo)
    negotiation = NegotiationService(gemini, attempt_repo, streak_service, cfg.difficulty)

    app.bot_data.update({
        "pool": pool,
        "attempt_repo": attempt_repo,
        "user_repo": user_repo,
        "streak_service": streak_service,
        "negotiation": negotiation,
        "difficulty_cfg": cfg.difficulty,
        "reminder_messages": cfg.reminder_messages,
    })


def main():
    cfg = load_config()
    app = (Application.builder()
           .token(cfg.telegram_token)
           .post_init(lambda a: _bootstrap(a, cfg))
           .build())

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("feedback", handlers.feedback))
    app.add_handler(CommandHandler("cancel", handlers.cancel))
    app.add_handler(CommandHandler("history", handlers.history_cmd))
    app.add_handler(CommandHandler("stats", handlers.stats_cmd))
    app.add_handler(CommandHandler("streak", handlers.streak_cmd))
    app.add_handler(CallbackQueryHandler(handlers.menu_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))

    if app.job_queue:
        app.job_queue.run_daily(daily_reminder, time=datetime.time(hour=cfg.reminder_hour_utc, minute=0))
    else:
        print("ВНИМАНИЕ: job-queue не установлен — напоминания не будут работать. "
              'Поставь: pip install "python-telegram-bot[job-queue]"')

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
