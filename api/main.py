import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from middlewares.cors import add_cors_middleware
from controllers.chat.routes import chat_router
from vectorstore.pinecone import PineconeVectorStore

# load datasets
from dataset.dataset import load_datasets

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Create document embeddings
datasets = load_datasets()
vector_store = PineconeVectorStore()
vector_store.create_embeddings(datasets)

app = FastAPI()
add_cors_middleware(app)

app.include_router(chat_router)

if __name__ == "__main__":
    # run main.py to debug backend
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
