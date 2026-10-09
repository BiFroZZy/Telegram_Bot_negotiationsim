# NegotiationSim

AI-тренажёр переговоров: Telegram-бот, который разыгрывает с пользователем переговоры
(закупщик, инвестор, клиент, препод, родители и т.д.), даёт разбор ошибок и отслеживает
прогресс через "индекс доверия партнёров" (стрик по дням).

## Структура проекта

```
negotiationsim/
├── cmd/app/main.py          # точка входа — сборка приложения и запуск polling
├── internal/
│   ├── config/config.py     # загрузка .env + configs/*.yaml
│   ├── domain/models.py     # доменные модели (Attempt, Streak)
│   ├── repository/          # доступ к PostgreSQL (asyncpg)
│   │   ├── db.py                  # пул соединений + миграции
│   │   ├── attempt_repository.py  # история попыток
│   │   └── user_repository.py     # стрик пользователя
│   ├── service/              # бизнес-логика
│   │   ├── gemini_service.py       # обращение к Gemini API
│   │   ├── streak_service.py       # логика индекса доверия
│   │   └── negotiation_service.py  # оркестрация сессии переговоров
│   ├── scenarios/            # кейсы переговоров, разбиты по темам
│   │   ├── business.py
│   │   ├── career.py
│   │   └── life.py
│   └── bot/                  # слой Telegram: хендлеры, клавиатуры, джобы
├── configs/                  # настройки без секретов (можно менять без деплоя кода)
│   ├── difficulty.yaml       # тексты и поведение для уровней сложности
│   └── reminder.yaml         # тексты ежедневных напоминаний
├── migrations/001_init.sql   # схема PostgreSQL
├── .env.example               # шаблон секретов (скопировать в .env)
├── docker-compose.yml         # локальный PostgreSQL одной командой
└── requirements.txt
```

## Быстрый старт (локально, с Docker)

```bash
cp .env.example .env
# впиши в .env: TELEGRAM_TOKEN (от @BotFather) и GEMINI_API_KEY (aistudio.google.com/apikey)

docker compose up -d          # поднимет PostgreSQL на localhost:5432
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m cmd.app.main        # запускает бота, миграции применятся автоматически
```

## Без Docker: бесплатная база в облаке (Supabase)

Если не хочешь ставить Docker — supabase.com, бесплатный тариф:
1. Создать проект (email, без карты)
2. Project Settings → Database → Connection string → скопировать URI
3. Вставить его в `.env` как `DATABASE_URL` вместо локального адреса
4. Дальше всё как в Quick Start, только без `docker compose up`

## Доступ к самой базе (посмотреть данные глазами)

- Через Docker: `docker compose exec postgres psql -U negotiationsim -d negotiationsim`
- Через Supabase: встроенный Table Editor в веб-интерфейсе проекта — данные видно сразу как таблицы
- Через любой GUI-клиент (TablePlus, DBeaver, pgAdmin) — просто вставить `DATABASE_URL` из `.env`

## Основные команды бота

- `/start` — выбрать категорию и сценарий
- `/feedback` — завершить текущие переговоры и получить разбор + оценку
- `/cancel` — выйти без сохранения
- `/history` — последние попытки
- `/stats` — средний балл, лучший результат, динамика
- `/streak` — статус индекса доверия партнёров
