import os
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from vectorstore.pinecone import PineconeVectorStore

class Agent:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model='gpt-4o-mini',
            temperature=0.0
        )
        pc = PineconeVectorStore()
        self.vector_store = pc.vector_store

    def run(self, query: str):
        vectorstore = self.vector_store.as_retriever()

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
        rag_chain = create_retrieval_chain(vectorstore, question_answer_chain)
        return rag_chain
