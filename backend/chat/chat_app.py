from __future__ import annotations as _annotations

import logfire
from chat.core.config import settings
from chat.db.base import Database
from chat.schemas.chat_messge import ChatMessage
from fastapi import Request
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.models.openai import OpenAIModel
from pydanticai.exceptons import UnexpectedModelBehavior

# 'if token-present' means nothing will be sent(and the example will work)
# if you don't have logfire configured


logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic()


model = OpenAIModel(
    "deepseek-chat",
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.BASE_URL,
)

agent = Agent(model)


async def get_db(request: Request) -> Database:
    return request.state.db


def to_chat_message(m: ModelMessage) -> ChatMessage:
    first_part = m.parts[0]

    if isinstance(m, ModelRequest):
        if isinstance(first_part, UserPromptPart):
            return {
                "role": "user",
                "timestamp": first_part.timestamp.isoformat(),
                "content": first_part.content,
            }
    elif isinstance(m, ModelResponse):
        if isinstance(first_part, TextPart):
            return {
                "role": "model",
                "timestamp": m.timestamp.isoformat(),
                "content": first_part.content,
            }
    raise UnexpectedModelBehavior(f"Unexpected message type of for chat app: {m}")
