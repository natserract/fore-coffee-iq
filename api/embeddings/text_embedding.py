import os
from pinecone import Pinecone
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from embeddings.dataset import data
from tqdm.auto import tqdm
from uuid import uuid4

def create_embeddings():
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    index = pc.Index(host=os.environ.get("PINECONE_INDEX_HOST") or '')

    model = 'text-embedding-ada-002'
    embeddings  = OpenAIEmbeddings(
        model=model,
    )
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    # Create document
    docs: list[Document] = []
    for item in tqdm(data, desc="Create document embeddings"):
        content = item["context"] + " " + item["question"]
        if item["answers"]["text"]:
            content += " " + " ".join(item["answers"]["text"])
        doc = Document(page_content=content, metadata={"id": item["id"]})
        docs.append(doc)

    vector_store.add_documents(documents=docs)
