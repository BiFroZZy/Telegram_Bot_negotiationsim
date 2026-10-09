"""Хендлеры команд и колбэков Telegram. Вся бизнес-логика — в internal/service."""
import random
import datetime
from telegram import Update
from telegram.ext import ContextTypes
from internal.scenarios import SCENARIOS, CATEGORY_TITLES
from internal.bot.keyboards import main_menu_keyboard, scenario_keyboard, difficulty_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤝 NegotiationSim\nВыбери направление тренировки:",
                                     reply_markup=main_menu_keyboard())


async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    difficulty_cfg = context.bot_data["difficulty_cfg"]
    negotiation = context.bot_data["negotiation"]

    if data == "menu":
        await query.edit_message_text("🤝 NegotiationSim\nВыбери направление тренировки:",
                                       reply_markup=main_menu_keyboard())
        return
    if data == "cat:random":
        key = random.choice(list(SCENARIOS.keys()))
        await query.edit_message_text(f"🎲 Выпал сценарий: {SCENARIOS[key]['title']}\n\nВыбери сложность:",
                                       reply_markup=difficulty_keyboard(key, difficulty_cfg))
        return
    if data.startswith("cat:"):
        cat = data.split(":")[1]
        await query.edit_message_text(f"{CATEGORY_TITLES[cat]}\nВыбери сценарий:",
                                       reply_markup=scenario_keyboard(cat))
        return
    if data.startswith("scn:"):
        key = data.split(":")[1]
        await query.edit_message_text(f"Сценарий: {SCENARIOS[key]['title']}\n\nВыбери сложность:",
                                       reply_markup=difficulty_keyboard(key, difficulty_cfg))
        return
    if data.startswith("diff:"):
        _, key, level = data.split(":")
        title = negotiation.start_session(query.message.chat_id, key, level)
        label = difficulty_cfg[level]["label"]
        await query.edit_message_text(
            f"Сценарий: {title}\nСложность: {label}\n\n"
            f"Начинай переговоры первым сообщением. Закончишь — /feedback. Передумал — /cancel.")
        return


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    negotiation = context.bot_data["negotiation"]
    if not negotiation.has_session(chat_id):
        await update.message.reply_text("Сначала выбери сценарий: /start")
        return
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    try:
        reply = await negotiation.reply(chat_id, update.message.text)
    except Exception as e:
        await update.message.reply_text(f"Ошибка ИИ: {e}")
        return
    await update.message.reply_text(reply)


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    negotiation = context.bot_data["negotiation"]
    streak_service = context.bot_data["streak_service"]
    if not negotiation.has_session(chat_id) or not negotiation.sessions[chat_id]["history"]:
        await update.message.reply_text("Диалога пока нет — начни через /start")
        return
    user = update.effective_user
    try:
        review, score, current, longest = await negotiation.finish(
            chat_id, user.id, user.username or user.first_name)
    except Exception as e:
        await update.message.reply_text(f"Ошибка ИИ: {e}")
        return
    score_line = f"\n\n⭐ Оценка: {score}/10" if score else ""
    word = streak_service.word_form(current)
    trust_msg = (f"\n\n✅ Сегодняшние переговоры прошли успешно!\n"
                 f"🤝 Индекс доверия партнёров: {current} {word} подряд\n{streak_service.trust_bar(current)}")
    await update.message.reply_text(f"📊 Разбор переговоров:\n\n{review}{score_line}{trust_msg}")
    await update.message.reply_text("Хочешь ещё раз? /start")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    negotiation = context.bot_data["negotiation"]
    if negotiation.cancel_session(update.message.chat_id):
        await update.message.reply_text("Сценарий отменён, без сохранения. /start — начать заново.")
    else:
        await update.message.reply_text("Активного сценария нет.")


async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attempt_repo = context.bot_data["attempt_repo"]
    difficulty_cfg = context.bot_data["difficulty_cfg"]
    rows = await attempt_repo.get_history(update.effective_user.id)
    if not rows:
        await update.message.reply_text("Пока нет завершённых попыток. Начни с /start")
        return
    lines = ["📜 Последние попытки:\n"]
    for r in rows:
        label = difficulty_cfg.get(r["difficulty"], {}).get("label", r["difficulty"])
        score = r["score"] if r["score"] is not None else "—"
        lines.append(f"• {r['finished_at'].strftime('%Y-%m-%d')} — {r['scenario_title']} ({label}) — ⭐ {score}/10")
    await update.message.reply_text("\n".join(lines))


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attempt_repo = context.bot_data["attempt_repo"]
    scores = await attempt_repo.get_scores(update.effective_user.id)
    if not scores:
        await update.message.reply_text("Пока нет данных для статистики. Пройди хотя бы одну тренировку: /start")
        return
    n = len(scores)
    avg = round(sum(scores) / n, 1)
    best = max(scores)
    trend = "➡️ стабильно"
    if n >= 2:
        half = n // 2 or 1
        first_avg = sum(scores[:half]) / half
        second_avg = sum(scores[half:]) / (n - half) if n - half > 0 else first_avg
        if second_avg > first_avg + 0.3:
            trend = "📈 прогресс растёт"
        elif second_avg < first_avg - 0.3:
            trend = "📉 есть просадка"
    await update.message.reply_text(
        f"📈 Твоя статистика:\n\nТренировок с оценкой: {n}\nСредний балл: {avg}/10\n"
        f"Лучший результат: {best}/10\nДинамика: {trend}")


async def streak_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_repo = context.bot_data["user_repo"]
    streak_service = context.bot_data["streak_service"]
    row = await user_repo.get_streak(update.effective_user.id)
    if not row:
        await update.message.reply_text("Индекс доверия ещё не запущен — пройди первую тренировку: /start")
        return
    current, longest, last_active = row["current_streak"], row["longest_streak"], row["last_active_date"]
    today_done = last_active == datetime.date.today()
    status = "✅ сегодня уже подтверждён" if today_done else "⚠️ сегодня ещё не подтверждён — успей до конца дня!"
    await update.message.reply_text(
        f"🤝 Индекс доверия партнёров\n\n{streak_service.trust_bar(current)}\n"
        f"Сейчас: {current} дней подряд (рекорд: {longest})\n{status}")
