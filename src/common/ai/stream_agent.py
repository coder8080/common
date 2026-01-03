import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from langchain.messages import AIMessageChunk
from langgraph.types import Command, Interrupt

from common.ai.langfuse import langfuse, langfuse_handler
from common.ai.types import Agent, chunk_metadata_adapter
from common.logging import logger


@dataclass
class StreamResponse:
    message_id: int


async def stream_agent(
    input: str | None,
    resume: None | dict[str, str | None],
    bot: Bot,
    agent: Agent,
    chat_id: int,
    state: FSMContext,
    interrupt_handler: Callable[
        [Interrupt, int, FSMContext, int], Awaitable[None]
    ]
    | None = None,
    context: dict[str, Any] = dict(),
) -> StreamResponse:
    if input is None and resume is None:
        ans = await bot.send_message(
            chat_id, "Не удалось вас понять, попробуйте написать текстом"
        )
        return StreamResponse(message_id=ans.message_id)

    message_id = (
        await bot.send_message(
            chat_id,
            "Подождите...",
            parse_mode="html",
            reply_markup=ReplyKeyboardRemove(),
        )
    ).message_id
    await bot.send_chat_action(chat_id, "typing")

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

    interrupts: list[Interrupt] = []

    async for stream_mode, data in agent.astream(
        input=(
            Command(resume=resume)
            if resume
            else {"messages": [{"role": "user", "content": input}]}
        ),
        config={
            "configurable": {"thread_id": chat_id},
            "callbacks": [langfuse_handler],
            "metadata": {
                "langfuse_user_id": f"admin-{chat_id}",
                "langfuse_session_id": f"admin-{chat_id}",
            },
        },
        context={**context, "chat_id": chat_id, "state": state},
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
                    interrupts.extend(update)
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

    for interrupt in interrupts:
        assert interrupt_handler, (
            f"Received interrupt {interrupt!r}, but no handler passed"
        )
        await interrupt_handler(interrupt, chat_id, state, message_id)

    return StreamResponse(message_id=message_id)
