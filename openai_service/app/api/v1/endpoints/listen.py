from fastapi import APIRouter, Depends, File, UploadFile
from typing import Optional
from app.core.security import get_api_key
from app.models.transcription import TranscriptionOptions

router = APIRouter()


@router.post("/transcription")
async def create_transcription(transcription: TranscriptionOptions, api_key: str = Depends(get_api_key)):
    """Преобразует аудио в текст"""
    return {"text": "transcribed_text"} 