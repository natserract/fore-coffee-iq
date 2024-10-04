import os
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from vectorstore.pinecone import PineconeVectorStore
from langchain_core.runnables import Runnable
from langchain_core.messages.ai import AIMessageChunk
from typing import AsyncGenerator, Callable, Dict, no_type_check, Any
from controllers.chat.models import ParsedRAGChunkResponse, RAGResponseMetadata
from controllers.chat.utils import parse_chunk_response, get_chunk_metadata

class Agent:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model='gpt-4o-mini',
            temperature=0.0
        )
        self.vector_store = PineconeVectorStore()

    def create_chain(self, query: str):
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        rag_chain = create_retrieval_chain(
            self.vector_store.retriever,
            question_answer_chain
        )
        return rag_chain

    @no_type_check
    async def ask_streaming(self, question: str) -> AsyncGenerator[ParsedRAGChunkResponse, ParsedRAGChunkResponse]:
        full_answer = ""
        async for response in self.answer_astream(question):
            if not response.last_chunk:
                yield response
            full_answer += response.answer

        yield response

    async def answer_astream(
        self,
        question: str,
        metadata: dict[str, str] = {}
    ) -> AsyncGenerator[ParsedRAGChunkResponse, ParsedRAGChunkResponse]:
        rolling_message = AIMessageChunk(content="")
        sources = []
        chunk_id = 0
        prev_answer = ""

        chain = self.create_chain(question)
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
