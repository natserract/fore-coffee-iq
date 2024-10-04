from agent import Agent
from langchain_core.runnables import Runnable
from langchain_core.messages.ai import AIMessageChunk
from typing import AsyncGenerator, Callable, Dict, no_type_check
from controllers.chat.models import ParsedRAGChunkResponse, RAGResponseMetadata
from controllers.chat.utils import parse_chunk_response, get_chunk_metadata

class ChatService:
    def __init__(self, agent: Agent) -> None:
        self._agent = agent;

    async def answer_astream(
        self,
        question: str,
        metadata: dict[str, str] = {}
    ) -> AsyncGenerator[ParsedRAGChunkResponse, ParsedRAGChunkResponse]:
        rolling_message = AIMessageChunk(content="")
        sources = []
        chunk_id = 0
        prev_answer = ""

        chain = self._agent.run(question)
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
    async def ask_streaming(self, question: str) -> AsyncGenerator[ParsedRAGChunkResponse, ParsedRAGChunkResponse]:
        full_answer = ""
        async for response in self.answer_astream(question):
            if not response.last_chunk:
                yield response
            full_answer += response.answer

        yield response
