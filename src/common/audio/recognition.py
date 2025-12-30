import os

import openai
from aiogram import Bot
from aiogram.types import Message

from common.env import get_str_env

openai_client = openai.OpenAI(api_key=get_str_env("OPENAI_API_KEY"))


async def transcribe(message: Message, bot: Bot):
    assert message.voice
    voice_file = await bot.get_file(message.voice.file_id)
    voice_path = f"temp_voice_{message.message_id}.ogg"

    assert voice_file.file_path

    await bot.download_file(voice_file.file_path, voice_path)
    # Конвертируем и распознаем
    with open(voice_path, "rb") as audio_file:
        text = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ru",
            response_format="text",
        )

    os.remove(voice_path)

    return text
