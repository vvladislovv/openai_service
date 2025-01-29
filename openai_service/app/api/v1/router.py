from fastapi import APIRouter, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.security import get_api_key
from app.api.v1.endpoints import chat, history, statistics, stats

# Здесь создается экземпляр маршрутизатора API с помощью APIRouter.
api_router = APIRouter()
# Создается экземпляр лимитера, который будет использоваться для ограничения частоты запросов.
limiter = Limiter(key_func=get_remote_address)

# Включаются маршруты для различных конечных точек API, таких как чат, история, статистика и статистика использования.
# Каждому маршруту присваивается префикс и теги, а также добавляется зависимость для проверки API-ключа.
api_router.include_router(chat.router, prefix="/chat", tags=["chat"], dependencies=[Depends(get_api_key)])
api_router.include_router(history.router, prefix="/history", tags=["history"], dependencies=[Depends(get_api_key)])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"], dependencies=[Depends(get_api_key)])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"], dependencies=[Depends(get_api_key)])
