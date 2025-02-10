import json
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import Response, StreamingResponse
from pydantic_ai.messages import ModelResponse, TextPart

from chat.chat_app import agent, get_db, to_chat_message
from chat.db.base import Database

router = APIRouter()


@router.get("/chat/")
async def get_chat(database: Database = Depends(get_db)) -> Response:
    msgs = await database.get_messages()
    return Response(
        b"\n".join(json.dumps(to_chat_message(m)).encode("utf-8") for m in msgs),
        media_type="text/plain",
    )


@router.post("/chat/")
async def post_chat(
    prompt: Annotated[str, Form()], database: Database = Depends(get_db)
) -> StreamingResponse:
    async def stream_messages():
        """Streams new line delimited JSON `Message`s to the client."""
        # stream the user prompt so that can be displayed straight away
        yield (
            json.dumps(
                {
                    "role": "user",
                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                    "content": prompt,
                }
            ).encode("utf-8")
            + b"\n"
        )
        # get the chat history so far to pass as context to the agent
        messages = await database.get_messages()
        # run the agent with the user prompt and the chat history
        async with agent.run_stream(prompt, message_history=messages) as result:
            async for text in result.stream(debounce_by=0.01):
                # text here is a `str` and the frontend wants
                # JSON encoded ModelResponse, so we create one
                m = ModelResponse(parts=[TextPart(text)], timestamp=result.timestamp())
                yield json.dumps(to_chat_message(m)).encode("utf-8") + b"\n"

        # add new messages (e.g. the user prompt and the agent response in this case) to the database
        await database.add_messages(result.new_messages_json())

    return StreamingResponse(stream_messages(), media_type="text/plain")
