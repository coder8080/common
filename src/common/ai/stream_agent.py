import asyncio
from datetime import datetime
from typing import Any

from aiogram import Bot
from aiogram.types import Message
from langchain.messages import AIMessageChunk

from src.common.ai.langfuse import langfuse, langfuse_handler
from src.common.ai.types import Agent, chunk_metadata_adapter
from src.common.logging import logger


async def stream_agent(
    input: str | None,
    message: Message,
    bot: Bot,
    agent: Agent,
    context: dict[str, Any] = dict(),
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

    async for stream_mode, data in agent.astream(
        input={"messages": [{"role": "user", "content": input}]},
        config={
            "configurable": {"thread_id": chat_id},
            "callbacks": [langfuse_handler],
            "metadata": {
                "langfuse_user_id": f"admin-{chat_id}",
                "langfuse_session_id": f"admin-{chat_id}",
            },
        },
        context=context,
        stream_mode=["messages", "updates"],
    ):
        if stream_mode == "messages":
            token, any_metadata = data
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
        elif stream_mode == "updates":
            if not isinstance(data, dict):
                logger.warning(f"Data is not a dict: {data!r}")
                continue

            for source, update in data.items():
                if source == "__interrupt__":
                    print(f"Received interrupt update: {update!r}")
        else:
            logger.error(f"Unexpected stream_mode: {stream_mode}")

    success = False
    tries = 5
    while not success and tries > 0:
        tries -= 1
        success = await update_response()
        if not success:
            await asyncio.sleep(rate_limit_seconds)

    langfuse.flush()
