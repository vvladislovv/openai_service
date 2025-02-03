from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import Optional
from app.core.security import get_api_key
from app.models.image import ImageGeneration
from app.models.chat import ImageGenerationRequest, ImageGenerationResponse
from app.services.openai import OpenAIService

router = APIRouter()
openai_service = OpenAIService()

@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """
    Генерирует изображение по описанию.
    
    Параметры:
        request: ImageGenerationRequest - Модель с данными для генерации изображения:
            - prompt: описание для генерации изображения
            - size: размер изображения (опционально)
    
    Возвращает:
        ImageGenerationResponse: URL сгенерированного изображения.
    
    Вызывает:
        HTTPException: При ошибках генерации изображения.
    """
    try:
        image_url = await openai_service.generate_image(request.prompt, request.size)
        return ImageGenerationResponse(image_url=image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit")
async def edit_image(
    image: UploadFile = File(...),
    mask: Optional[UploadFile] = File(None),
    prompt: str = None,
    api_key: str = Depends(get_api_key)
):
    """Редактирует изображение (заглушка)"""
    return {"status": "not implemented"} 