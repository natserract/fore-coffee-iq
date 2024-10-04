from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers.chat.dto import ChatQuestion

chat_router = APIRouter()

@chat_router.post("/chat", tags=["Chat"])
async def create_chat_handler(
    request: Request,
    chat_question: ChatQuestion,
):
    json_compatible_item_data = jsonable_encoder(chat_question)
    return JSONResponse(content=json_compatible_item_data)
