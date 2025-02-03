from fastapi import APIRouter, Depends
from app.core.security import get_api_key
from app.api.v1.endpoints import (
    chat,
    images,
    speech,
    listen,
    history,
    statistics
)

# Здесь создается экземпляр маршрутизатора API с помощью APIRouter.
api_router = APIRouter()

# Включаются маршруты для различных конечных точек API, таких как чат, история, статистика и статистика использования.
# Каждому маршруту присваивается префикс и теги, а также добавляется зависимость для проверки API-ключа.
api_router.include_router(chat.router, prefix="/chat", tags=["chat"], dependencies=[Depends(get_api_key)])
api_router.include_router(images.router, prefix="/images", tags=["images"], dependencies=[Depends(get_api_key)])
api_router.include_router(speech.router, prefix="/speech", tags=["speech"], dependencies=[Depends(get_api_key)])
api_router.include_router(listen.router, prefix="/listen", tags=["listen"], dependencies=[Depends(get_api_key)])
api_router.include_router(history.router, prefix="/history", tags=["history"], dependencies=[Depends(get_api_key)])


api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"], dependencies=[Depends(get_api_key)])