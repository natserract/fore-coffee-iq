import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from middlewares.cors import add_cors_middleware
from controllers.chat.routes import chat_router

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI()
add_cors_middleware(app)

app.include_router(chat_router)

if __name__ == "__main__":
    # run main.py to debug backend
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
