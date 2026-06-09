# Status BOT

Telegram-бот с AI-помощником для справочных вопросов по АО «Регистраторское общество «СТАТУС».

Бот отвечает на общие вопросы о контактах, режиме работы, онлайн-кабинете,
формах документов и маршрутизации обращений. По юридическим, инвестиционным,
налоговым и персональным вопросам бот направляет пользователя в официальные
каналы АО «СТАТУС».

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

## Где взять Telegram-токен

1. Откройте в Telegram `@BotFather`.
2. Выполните команду `/newbot`.
3. Скопируйте выданный токен в `.env`:

```env
TELEGRAM_BOT_TOKEN=1234567890:telegram_token_here
```

## Проверка

```bash
python -m compileall src
```

## Источники справочного контекста

- официальный сайт АО «СТАТУС»: https://rostatus.ru/
- контакты центрального офиса: https://rostatus.ru/about/contact/
- СТАТУС Онлайн: https://online.rostatus.ru/
- формы анкет и распоряжений: https://rostatus.ru/about/ed/forms-of-forms-and-orders-for-registered-persons/
- документация Polza.ai: https://polza.ai/docs/gaidy/chat-completions
