import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from middlewares.cors import add_cors_middleware
from controllers.chat.routes import chat_router
from dataset.data import data
from vectorstore.pinecone import PineconeVectorStore

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Create document embeddings
vector_store = PineconeVectorStore()
vector_store.create_embeddings(data)

app = FastAPI()
add_cors_middleware(app)

app.include_router(chat_router)

if __name__ == "__main__":
    # run main.py to debug backend
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
