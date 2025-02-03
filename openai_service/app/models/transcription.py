from pydantic import BaseModel
from typing import Optional

class TranscriptionOptions(BaseModel):
    """Класс для опций транскрипции, включает идентификатор чата, язык и формат ответа."""
    chat_id: str
    language: Optional[str] = None
    response_format: Optional[str] = "text" 