import os
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

def run(q: str):
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    index = pc.Index(host=os.environ.get("PINECONE_INDEX_HOST") or '')

    model = 'text-embedding-ada-002'
    embeddings  = OpenAIEmbeddings(
        model=model,
    )
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    results = vector_store.similarity_search_with_score(
        q, k=3
    )
    for res, score in results:
        print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")
    return vector_store

    """
    results = vector_store.similarity_search_with_score(
        query, k=3
    )
    for res, score in results:
        print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")
    """
