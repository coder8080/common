from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from .recognition import transcribe


class RecognitionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        update: TelegramObject,
        data: Dict[str, Any],
    ):
        assert isinstance(update, Update)
        bot = update.bot
        assert bot
        try:
            if update.message and update.message.text:
                data["input"] = update.message.text
            elif update.message and update.message.voice:
                data["input"] = await transcribe(update.message, bot)
            else:
                data["input"] = None
        except Exception as e:
            print(e)
            data["input"] = None

        return await handler(update, data)
