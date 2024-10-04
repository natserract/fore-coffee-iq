import os
from uuid import uuid4, UUID
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA, create_retrieval_chain
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
from datetime import datetime

chat_history = {}

today_date = datetime.now().strftime("%B %d, %Y")

class Agent:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model='gpt-4o-mini',
            temperature=0.0
        )
        self.vector_store = PineconeVectorStore()

    def create_chain(self):
        retriever = self.vector_store.retriever;

        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, contextualize_q_prompt
        )

        system_prompt = f"""
        Your name is NatserractIQ. You are an assistant for question-answering tasks. Today's date is {today_date}.

        Use the following pieces of retrieved context to answer the question.
        If you don't know the answer with the context provided, say that you don't know, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer concise.
        """
        system_prompt += "\n\n {context}"

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
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

        chain = self.create_chain()
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
