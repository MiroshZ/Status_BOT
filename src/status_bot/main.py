import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from status_bot.ai import PolzaAiClient
from status_bot.config import get_settings
from status_bot.handlers import setup_handlers
from status_bot.knowledge import SYSTEM_PROMPT


async def main() -> None:
    settings = get_settings()
    handlers: list[logging.Handler]
    if settings.log_file:
        log_path = Path(settings.log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers = [
            RotatingFileHandler(
                log_path,
                maxBytes=2_000_000,
                backupCount=4,
                encoding="utf-8",
            )
        ]
    else:
        handlers = [logging.StreamHandler()]
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )

    bot = Bot(
        token=settings.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(),
    )
    dispatcher = Dispatcher()

    ai_client = PolzaAiClient(
        api_key=settings.polza_api_key.get_secret_value(),
        base_url=settings.polza_base_url,
        model=settings.polza_model,
        system_prompt=SYSTEM_PROMPT,
    )
    dispatcher.include_router(setup_handlers(ai_client))

    try:
        await dispatcher.start_polling(bot)
    finally:
        await ai_client.close()
        await bot.session.close()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
