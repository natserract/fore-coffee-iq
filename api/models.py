from pydantic import BaseModel
from typing import List, Optional, Any

class ChatLLMMetadata(BaseModel):
    name: str
    display_name: str | None = None
    description: str | None = None
    image_url: str | None = None
    brain_id: str | None = None
    brain_name: str | None = None

class RAGResponseMetadata(BaseModel):
    citations: list[int] | None = None
    followup_questions: list[str] | None = None
    sources: list[Any] | None = None
    metadata_model: ChatLLMMetadata | None = None

class ParsedRAGChunkResponse(BaseModel):
    answer: str
    metadata: RAGResponseMetadata
    last_chunk: bool = False
