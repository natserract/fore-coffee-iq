"""
import os
import json
import datetime
from openai import OpenAI, AsyncOpenAI
from fastapi import FastAPI,Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import AsyncGenerator, Dict, no_type_check
from pydantic import BaseModel
from agent import agent
from dto import GetChatHistoryOutput
from uuid import UUID, uuid4
from utils import parse_chunk_response, get_chunk_metadata
from langchain_core.messages.ai import AIMessageChunk
from models import ParsedRAGChunkResponse, RAGResponseMetadata

load_dotenv(verbose=True, override=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

class Chat(BaseModel):
    question: str

async def answer_astream(question: str,  metadata: dict[str, str] = {}) -> AsyncGenerator[ParsedRAGChunkResponse, ParsedRAGChunkResponse]:
    rolling_message = AIMessageChunk(content="")
    sources = []
    chunk_id = 0
    prev_answer = ""

    chain = agent(question)
    async for chunk in chain.astream({"input": question }, config={"metadata": metadata},):
        if "docs" in chunk:
            sources = chunk["docs"] if "docs" in chunk else []

        if "answer" in chunk:
            rolling_message, answer_str = parse_chunk_response(
                rolling_message,
                chunk,
                True,
            )

            if len(answer_str) > 0:
                parsed_chunk = ParsedRAGChunkResponse(
                    answer=answer_str,
                    metadata=RAGResponseMetadata(),
                )
                yield parsed_chunk
                chunk_id += 1

    last_chunk = ParsedRAGChunkResponse(
        answer="",
        metadata=get_chunk_metadata(rolling_message, sources),
        last_chunk=True,
    )
    yield last_chunk

@no_type_check
async def ask_streaming(question: str) -> AsyncGenerator[ParsedRAGChunkResponse, ParsedRAGChunkResponse]:
    full_answer = ""
    async for response in answer_astream(question):
        if not response.last_chunk:
            yield response
        full_answer += response.answer

    yield response

#@app.post("/chat")
async def ask(req: Chat):
    question = req.question
    #chain = agent(question)

    message_metadata = {
        "chat_id": uuid4(),
        "message_id": uuid4(),  # do we need it ?,
        "user_message": question,  # TODO: define result
        "message_time": datetime.datetime.now(),  # TODO: define result
        "prompt_title": "",
        # brain_name and brain_id must be None in the chat-with-llm case, as this will force the front to look for the model_metadata
        "brain_name": 'Natserract brain',
        "brain_id": None,
    }

    @no_type_check
    async def generator():
        full_answer = ""

        async for response in ask_streaming(
            question=question
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

"""
