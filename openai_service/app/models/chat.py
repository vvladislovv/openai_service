from pydantic import BaseModel
from typing import List, Optional, Union


class ChatCreate(BaseModel):
    """Класс для создания нового чата. Включает в себя имя чата, вопрос пользователя, модель GPT, ответ, контекст и количество токенов."""
    chat_name: str 
    question: str  
    model_gpt: str
    answer: str  
    context: str 
    token: int 

class ChatRename(BaseModel):
    """Класс для переименования чата. Включает в себя идентификатор чата и новое название."""
    chat_id: str  
    new_name: str  

class Message(BaseModel):
    """Класс для сообщения в чате. Включает в себя роль и содержание сообщения."""
    role: str  
    content: str  

class ChatCompletion(BaseModel):
    """Класс для завершения чата. Включает в себя идентификатор чата, модель, сообщения (опционально), URL изображения (опционально) и URL аудиофайла (опционально)."""
    chat_id: str  
    model: str  
    messages: Optional[List[dict]] = None  
    image_url: Optional[str] = None  
    audio_file: Optional[str] = None  

class ChatRequest(BaseModel):
    """Класс для запроса в чате. Включает в себя идентификатор чата, модель и сообщения."""
    chat_id: str  
    model: str  
    messages: List[Message]  

class ChatResponse(BaseModel):
    """Класс для ответа из чата. Включает в себя идентификатор, модель, время создания, ответ и количество использованных токенов."""
    id: str  
    model: str  
    created: int  
    response: str  
    tokens_used: int  
    
    class Config:
        from_attributes = True

class ChatWithContextRequest(ChatRequest):
    """Класс для запроса в чате с контекстом. Включает в себя идентификатор чата, модель, сообщения и идентификатор сессии."""
    session_id: str  

class SpeechRequest(BaseModel):
    """Класс для запроса на транскрипцию аудиофайла. Включает в себя путь к аудиофайлу."""
    audio_file: str  

class TranscriptionResponse(BaseModel):
    """Класс для ответа на транскрипцию аудиофайла. Включает в себя результат транскрипции."""
    transcription: str  

class ImageGenerationRequest(BaseModel):
    """Класс для запроса на генерацию изображения. Включает в себя описание и размер изображения (опционально)."""
    prompt: str  
    size: Optional[str] = "1024x1024"  

class ImageGenerationResponse(BaseModel):
    """Класс для ответа на генерацию изображения. Включает в себя URL сгенерированного изображения."""
    image_url: str  