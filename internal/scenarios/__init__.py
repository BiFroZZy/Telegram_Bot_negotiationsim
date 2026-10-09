"""Единая точка доступа ко всем сценариям (кейсам) переговоров."""
from internal.scenarios.business import SCENARIOS as BUSINESS_SCENARIOS
from internal.scenarios.career import SCENARIOS as CAREER_SCENARIOS
from internal.scenarios.life import SCENARIOS as LIFE_SCENARIOS

SCENARIOS = {**BUSINESS_SCENARIOS, **CAREER_SCENARIOS, **LIFE_SCENARIOS}

CATEGORY_TITLES = {
    "business": "💼 Бизнес и переговоры",
    "career": "🎓 Учёба и карьера",
    "life": "🎭 Бытовые (для настроения)",
}
