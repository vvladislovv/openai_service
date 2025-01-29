from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.security import get_api_key

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
@router.get("/")
@limiter.limit("5/minute")  # Ограничение: 5 запросов в минуту
async def get_stats(request: Request, api_key: str = Depends(get_api_key)):
    """
    Обрабатывает запрос на получение статистики.

    Эта функция возвращает сообщение о доступности конечной точки статистики
    и передает API-ключ, используемый для аутентификации. 
    Ограничение на количество запросов составляет 5 запросов в минуту.

    Параметры:
        request (Request): Объект запроса FastAPI.
        api_key (str): API-ключ, полученный через зависимость.

    Возвращает:
        dict: Словарь с сообщением и API-ключом.
    """
    return {"message": "Statistics endpoint", "api_key": api_key}
