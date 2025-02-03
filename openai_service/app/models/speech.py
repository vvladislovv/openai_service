from pydantic import BaseModel
from typing import Optional

class SpeechCreate(BaseModel):
    """Класс для создания аудио из текста, включает идентификатор чата, текст, голос, модель и формат ответа."""
    chat_id: str
    text: str
    voice: Optional[str] = "alloy"
    model: Optional[str] = "tts-1"
    response_format: Optional[str] = "mp3" 