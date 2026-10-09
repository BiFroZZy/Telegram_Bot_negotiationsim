"""Inline-клавиатуры Telegram-бота."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from internal.scenarios import SCENARIOS


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💼 Бизнес и переговоры", callback_data="cat:business")],
        [InlineKeyboardButton("🎓 Учёба и карьера", callback_data="cat:career")],
        [InlineKeyboardButton("🎭 Бытовые (для настроения)", callback_data="cat:life")],
        [InlineKeyboardButton("🎲 Случайный сценарий", callback_data="cat:random")],
    ])


def scenario_keyboard(category: str):
    items = [(k, v) for k, v in SCENARIOS.items() if v["category"] == category]
    buttons = [[InlineKeyboardButton(v["title"], callback_data=f"scn:{k}")] for k, v in items]
    buttons.append([InlineKeyboardButton("‹ Назад", callback_data="menu")])
    return InlineKeyboardMarkup(buttons)


def difficulty_keyboard(key: str, difficulty_cfg: dict):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(difficulty_cfg[level]["label"], callback_data=f"diff:{key}:{level}")]
        for level in ("easy", "medium", "hard")
    ])
