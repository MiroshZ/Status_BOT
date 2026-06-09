import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from status_bot.ai import PolzaAiClient
from status_bot.config import get_settings
from status_bot.handlers import setup_handlers
from status_bot.knowledge import SYSTEM_PROMPT


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    bot = Bot(
        token=settings.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()

    ai_client = PolzaAiClient(
        api_key=settings.polza_api_key.get_secret_value(),
        base_url=settings.polza_base_url,
        model=settings.polza_model,
        system_prompt=SYSTEM_PROMPT,
    )
    dispatcher.include_router(setup_handlers(ai_client))

    await dispatcher.start_polling(bot)


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
