import asyncio
from datetime import datetime

from aiogram import Bot
from aiogram.types import Message
from langchain.messages import AIMessageChunk

from .langfuse import langfuse, langfuse_handler
from .types import Agent, chunk_metadata_adapter


async def stream_agent(
    input: str | None, message: Message, bot: Bot, agent: Agent
):
    if input is None:
        await message.answer(
            "Не удалось вас понять, попробуйте написать текстом"
        )
        return

    chat_id = message.chat.id
    message_id = (
        await message.answer("Подождите...", parse_mode="html")
    ).message_id
    await bot.send_chat_action(message.chat.id, "typing")

    rate_limit_seconds = 0.3
    last_updated_at = datetime.now().timestamp() - rate_limit_seconds * 2
    result_text = ""

    async def update_response():
        try:
            await asyncio.wait_for(
                bot.edit_message_text(
                    result_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    parse_mode="html",
                ),
                timeout=2,
            )
            return True
        except Exception:
            return False

    async for token, any_metadata in agent.astream(
        input={"messages": [{"role": "user", "content": input}]},
        config={
            "configurable": {"thread_id": chat_id},
            "callbacks": [langfuse_handler],
            "metadata": {
                "langfuse_user_id": f"admin-{chat_id}",
                "langfuse_session_id": f"admin-{chat_id}",
            },
        },
        stream_mode="messages",
    ):
        if not isinstance(token, AIMessageChunk):
            continue
        metadata = chunk_metadata_adapter.validate_python(any_metadata)
        node = metadata.langgraph_node
        if node == "model":
            for content in token.content_blocks:
                if content["type"] == "text":
                    result_text += content["text"]
                    if (
                        datetime.now().timestamp() - last_updated_at
                        >= rate_limit_seconds
                    ):
                        success = await update_response()
                        if success:
                            last_updated_at = datetime.now().timestamp()

    success = False
    tries = 5
    while not success and tries > 0:
        tries -= 1
        success = await update_response()
        if not success:
            await asyncio.sleep(rate_limit_seconds)

    langfuse.flush()
