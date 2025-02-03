from fastapi import APIRouter, Depends, HTTPException
from app.models.speech import SpeechCreate
from app.core.security import get_api_key
from app.models.chat import SpeechRequest, TranscriptionResponse
from app.services.openai import OpenAIService

router = APIRouter()
openai_service = OpenAIService()


@router.post("/create")
async def create_speech(speech: SpeechCreate, api_key: str = Depends(get_api_key)):
    """Создает аудио из текста"""
    return {"audio_url": "generated_audio_url"}

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: SpeechRequest):
    """
    Транскрибирует аудиофайл в текст.
    
    Параметры:
        request: SpeechRequest - Модель с данными для транскрипции:
            - audio_file: путь к аудиофайлу
    
    Возвращает:
        TranscriptionResponse: Результат транскрипции.
    
    Вызывает:
        HTTPException: При ошибках обработки аудиофайла.
    """
    try:
        transcription = await openai_service.transcribe_audio(request.audio_file)
        return TranscriptionResponse(transcription=transcription)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 