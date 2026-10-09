"""Фоновые задачи бота: ежедневное напоминание про 'индекс доверия'."""
import datetime
from telegram.ext import ContextTypes


async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    user_repo = context.bot_data["user_repo"]
    streak_service = context.bot_data["streak_service"]
    messages = context.bot_data["reminder_messages"]
    today = datetime.date.today()
    rows = await user_repo.all_streaks()
    for row in rows:
        user_id, current, last_active = row["user_id"], row["current_streak"], row["last_active_date"]
        if last_active == today:
            continue
        if current > 0:
            word = streak_service.word_form(current)
            text = messages["streak_at_risk"].format(streak=current, streak_word=word)
        else:
            text = messages["no_streak_yet"]
        try:
            await context.bot.send_message(chat_id=user_id, text=text)
        except Exception:
            pass
