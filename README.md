# Status BOT

Telegram-бот с AI-помощником для справочных вопросов по АО «Регистраторское общество «СТАТУС».

## Быстрый старт

1. Создайте виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Установите зависимости:

```bash
pip install -e .
```

3. Создайте `.env` на основе `.env.example` и заполните:

```bash
cp .env.example .env
```

4. Запустите бота:

```bash
status-bot
```

## Переменные окружения

- `TELEGRAM_BOT_TOKEN` - токен Telegram-бота от BotFather.
- `POLZA_API_KEY` - API-ключ Polza.ai.
- `POLZA_BASE_URL` - базовый URL OpenAI-compatible API Polza.ai.
- `POLZA_MODEL` - модель Polza.ai, например `openai/gpt-4o`.
- `LOG_LEVEL` - уровень логирования.
