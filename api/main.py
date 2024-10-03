from dotenv import load_dotenv
from embeddings.text_embedding import create_embeddings
from agent import agent
from server import app

load_dotenv(verbose=True, override=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
