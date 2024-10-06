import os
from uuid import uuid4, UUID
from datetime import datetime
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain.retrievers import MergerRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from vectorstore.pinecone import PineconeVectorStore
from langchain_core.runnables import Runnable
from langchain_core.messages import AIMessageChunk, AIMessage, HumanMessage
from typing import AsyncGenerator, Callable, Dict, no_type_check, Any
from controllers.chat.models import ParsedRAGChunkResponse, RAGResponseMetadata
from controllers.chat.utils import parse_chunk_response, get_chunk_metadata
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from prompt.system_prompt import (
    system_prompt_template as main_prompt_template,
    contextualize_q_system_prompt_template
)
from utils.prompt_template_parser import PromptTemplateParser

chat_history = {}

today_date = datetime.now().strftime("%B %d, %Y")

class Agent:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model='gpt-4o',
            temperature=0.0
        )
        self.vector_store = PineconeVectorStore()

    def create_chain(self, query: str):
        documents = self.vector_store.filter_documents(query)
        retriever = self.create_retriever(documents)

        system_prompt_template = PromptTemplateParser(
            template=main_prompt_template
        )
        system_prompt = system_prompt_template.format({
            "today_date": today_date,
            "question": query,
        })
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt_template),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, contextualize_q_prompt
        )

        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        rag_chain = create_retrieval_chain(
            history_aware_retriever,
            question_answer_chain
        )

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        return conversational_rag_chain

    def create_retriever(
        self, documents: list[Document]
    ) -> MergerRetriever:
        vector_store_retriever = self.vector_store.retriever

        retrievers = [
            vector_store_retriever,
            BM25Retriever.from_documents(documents),
        ]

        return MergerRetriever(retrievers=retrievers)

    @no_type_check
    async def ask_streaming(
        self,
        question: str,
    ) -> AsyncGenerator[ParsedRAGChunkResponse, ParsedRAGChunkResponse]:
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

        chain = self.create_chain(query=question)
        async for chunk in chain.astream(
            {"input": question },
            config={
                "metadata": metadata,
                "configurable": {"session_id": "Natserract"}
            }
        ):
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

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in chat_history:
            chat_history[session_id] = ChatMessageHistory()
        return chat_history[session_id]
