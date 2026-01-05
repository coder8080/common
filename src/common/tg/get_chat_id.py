from aiogram.types import Update


def get_chat_id(update: Update) -> int | None:
    if update.message:
        return update.message.chat.id
    elif update.callback_query and update.callback_query.message:
        return update.callback_query.message.chat.id
    return None
