from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove


async def remove_keyboard(bot: Bot, chat_id: int):
    message = await bot.send_message(
        chat_id, "🧹 Убираю кнопки...", reply_markup=ReplyKeyboardRemove()
    )
    await bot.delete_message(chat_id, message.message_id)
