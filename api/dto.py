from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

class GetChatHistoryOutput(BaseModel):
    chat_id: UUID
    message_id: UUID
    user_message: str
    message_time: datetime
    assistant: str | None = None
    prompt_title: str | None = None
    brain_name: str | None = None
    brain_id: UUID | None = None  # string because UUID is not JSON serializable
    metadata: Optional[dict] | None = None
    thumbs: Optional[bool] | None = None

    def dict(self, *args, **kwargs):
        chat_history = super().dict(*args, **kwargs)
        chat_history["chat_id"] = str(chat_history.get("chat_id"))
        chat_history["message_id"] = str(chat_history.get("message_id"))

        return chat_history
