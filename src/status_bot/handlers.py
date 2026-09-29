from collections.abc import Awaitable, Callable
import logging

from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from status_bot.ai import AiServiceError, PolzaAiClient

MAX_TELEGRAM_MESSAGE_LENGTH = 4096

logger = logging.getLogger(__name__)


def split_message(text: str, limit: int = MAX_TELEGRAM_MESSAGE_LENGTH) -> list[str]:
    if limit <= 0:
        raise ValueError("limit must be positive")

    if _telegram_length(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    while _telegram_length(remaining) > limit:
        split_at = _find_split_point(remaining, limit, "\n")
        if split_at < 0:
            split_at = _find_split_point(remaining, limit, " ")
        if split_at < 0:
            split_at = _codepoint_index_at_limit(remaining, limit)
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()

    if remaining:
        chunks.append(remaining)
    return chunks


def _telegram_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def _find_split_point(text: str, limit: int, separator: str) -> int:
    end = _codepoint_index_at_limit(text, limit)
    split_at = text.rfind(separator, 0, end)
    return split_at if split_at >= end // 2 else -1


def _codepoint_index_at_limit(text: str, limit: int) -> int:
    units = 0
    for index, char in enumerate(text):
        char_units = 2 if ord(char) > 0xFFFF else 1
        if units + char_units > limit:
            if index == 0:
                raise ValueError("limit is too small for this character")
            return index
        units += char_units
    return len(text)


async def answer_long(message: Message, text: str) -> None:
    for chunk in split_message(text):
        await message.answer(chunk)


def setup_handlers(ai_client: PolzaAiClient) -> Router:
    ask_ai: Callable[[str], Awaitable[str]] = ai_client.ask
    router = Router()

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        await message.answer(
            "Здравствуйте! Я AI-помощник по справочным вопросам АО «СТАТУС».\n\n"
            "Могу подсказать контакты, режим работы, где искать формы документов, "
            "как пользоваться онлайн-кабинетом и куда направить обращение. "
            "Напишите ваш вопрос обычным сообщением."
        )

    @router.message(Command("help"))
    async def help_command(message: Message) -> None:
        await message.answer(
            "Примеры вопросов:\n"
            "- Где находится центральный офис?\n"
            "- Как работает операционный зал?\n"
            "- Где найти формы анкет и распоряжений?\n"
            "- Можно ли через регистратора продать акции?\n\n"
            "По персональным операциям и документам лучше сверяться с официальным "
            "сайтом rostatus.ru или обращаться в офис АО «СТАТУС»."
        )

    @router.message()
    async def handle_text(message: Message) -> None:
        if not message.text:
            await message.answer("Пока я умею отвечать только на текстовые вопросы.")
            return

        async with ChatActionSender(
            action=ChatAction.TYPING,
            bot=message.bot,
            chat_id=message.chat.id,
        ):
            try:
                answer = await ask_ai(message.text)
            except AiServiceError:
                logger.exception("AI provider request failed")
                await message.answer(
                    "Сейчас не получилось получить ответ от AI-сервиса. "
                    "Попробуйте повторить запрос чуть позже."
                )
                return

        await answer_long(message, answer)

    return router
