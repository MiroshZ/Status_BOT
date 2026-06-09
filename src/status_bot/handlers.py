from collections.abc import Awaitable, Callable

from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from status_bot.ai import AiServiceError, PolzaAiClient

MAX_TELEGRAM_MESSAGE_LENGTH = 4096

router = Router()


def split_message(text: str, limit: int = MAX_TELEGRAM_MESSAGE_LENGTH) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit)
        if split_at < limit // 2:
            split_at = remaining.rfind(" ", 0, limit)
        if split_at < limit // 2:
            split_at = limit
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()

    if remaining:
        chunks.append(remaining)
    return chunks


async def answer_long(message: Message, text: str) -> None:
    for chunk in split_message(text):
        await message.answer(chunk)


def setup_handlers(ai_client: PolzaAiClient) -> Router:
    ask_ai: Callable[[str], Awaitable[str]] = ai_client.ask

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

        async with ChatActionSender(action=ChatAction.TYPING, chat_id=message.chat.id):
            try:
                answer = await ask_ai(message.text)
            except AiServiceError:
                await message.answer(
                    "Сейчас не получилось получить ответ от AI-сервиса. "
                    "Попробуйте повторить запрос чуть позже."
                )
                return

        await answer_long(message, answer)

    return router
