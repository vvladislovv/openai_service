from pydantic import BaseModel
from typing import Optional

class ImageGeneration(BaseModel):
    """Класс для генерации изображений, включает идентификатор чата, текст запроса, размер, качество и количество изображений."""
    chat_id: str
    prompt: str
    size: Optional[str] = "1024x1024"
    quality: Optional[str] = "standard"
    n: Optional[int] = 1 