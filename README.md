# 💰 Finance Bot — Учёт расходов через Telegram

Автоматически читает уведомления от **cardxabar**, категоризирует траты с помощью ИИ и строит красивую статистику.

## Как работает

```
cardxabar → Telethon userbot → твой Finance Bot → SQLite база
                                      ↓
                              ИИ (Claude) угадывает категорию
                                      ↓
                              ты подтверждаешь / выбираешь
                                      ↓
                              бот запоминает магазин → категория
```

После нескольких подтверждений бот начинает **полностью автоматически** определять категории без вопросов.

---

## Быстрый старт

### 1. Создай бота
- Открой [@BotFather](https://t.me/BotFather) → `/newbot`
- Скопируй токен

### 2. Узнай свой Telegram ID
- Напиши [@userinfobot](https://t.me/userinfobot)
- Скопируй число (например `123456789`)

### 3. Получи API ключи Telegram
- Зайди на [my.telegram.org](https://my.telegram.org)
- Apps → Create new application
- Скопируй `api_id` и `api_hash`

### 4. Получи Claude API ключ
- Зайди на [console.anthropic.com](https://console.anthropic.com)
- API Keys → Create Key

### 5. Настрой переменные окружения
```bash
cp .env.example .env
# Заполни .env своими данными
```

### 6. Запусти локально
```bash
pip install -r requirements.txt

# Первый запуск userbot — введёт номер телефона и код
python userbot.py

# В другом терминале
python bot.py
```

---

## Деплой на Railway

1. Залей проект на GitHub
2. Зайди на [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. В Variables добавь все переменные из `.env.example`
4. Railway автоматически запустит оба процесса из `Procfile`

> ⚠️ **Важно для userbot на Railway**: при первом запуске нужно локально запустить `python userbot.py` и пройти авторизацию (введёшь номер + код из Telegram). Это создаст файл `finance_userbot.session` — загрузи его в Railway как файл или используй переменную `SESSION_STRING` (см. Telethon StringSession).

---

## Команды бота

| Команда | Что делает |
|---------|-----------|
| `/start` | Приветствие и инструкция |
| `/stats` | Статистика текущего месяца + пирог 🥧 |
| `/recent` | Последние 10 операций |
| `/categories` | Все известные магазины |

В `/stats` есть кнопки:
- **◀️ ▶️** — навигация по месяцам
- **📊 По дням** — столбчатый график по дням

---

## Структура проекта

```
finance_bot/
├── bot.py              # Точка входа бота
├── userbot.py          # Telethon userbot (авто-форвард)
├── config.py           # Конфигурация
├── requirements.txt
├── Procfile            # Для Railway
├── handlers/
│   ├── transactions.py # Приём и категоризация транзакций
│   ├── stats.py        # Статистика и графики
│   └── categories.py   # Управление категориями
└── utils/
    ├── database.py     # SQLite операции
    ├── parser.py       # Парсинг сообщений cardxabar
    ├── ai_categories.py # Категоризация через Claude API
    └── charts.py       # Генерация графиков
```
