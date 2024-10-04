import datetime
from uuid import UUID, uuid4
from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from controllers.chat.dto import ChatQuestion, GetChatHistoryOutput
from typing import no_type_check
from controllers.chat.service import ChatService

chat_router = APIRouter()

@chat_router.post("/chat", tags=["Chat"])
async def create_chat_handler(
    request: Request,
    chat_question: ChatQuestion,
):
    chat_service = ChatService()

    message_metadata = {
        "chat_id": uuid4(),
        "message_id": uuid4(),
        "user_message": chat_question.question,
        "message_time": datetime.datetime.now(),
        "prompt_title": "",
        "brain_name": 'Natserract brain',
        "brain_id": None,
    }

    @no_type_check
    async def generator():
        full_answer = ""

        async for response in chat_service.ask_streaming(
            question=chat_question.question
        ):
            # Format output to be correct servicedf;j
            if not response.last_chunk:
                streamed_chat_history = GetChatHistoryOutput(
                    assistant=response.answer,
                    metadata=response.metadata.model_dump(),
                    **message_metadata,
                )

                full_answer += response.answer
                yield f"data: {streamed_chat_history.model_dump_json()}"

        streamed_chat_history = GetChatHistoryOutput(
            assistant=response.answer,
            metadata=response.metadata.model_dump(),
            **message_metadata,
        )
        yield f"data: {streamed_chat_history.model_dump_json()}"

    response_messages = generator()
    return StreamingResponse(response_messages, media_type="application/x-ndjson")
