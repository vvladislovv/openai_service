from fastapi import APIRouter, HTTPException
from app.models.history import StatisticsResponse
from app.db.database import get_statistics
from app.core.logging import logs_bot

router = APIRouter()

@router.get("", response_model=StatisticsResponse)
async def get_usage_statistics():
    """
    Получает статистику использования из базы данных.

    Эта функция вызывает метод `get_statistics`, чтобы получить текущую
    статистику. Если запрос успешен, она возвращает статистику. В случае
    ошибки функция записывает сообщение об ошибке и вызывает исключение HTTP 500.

    Returns:
        StatisticsResponse: Данные статистики, полученные из базы данных.
    """
    try:
        stats = await get_statistics()
        return stats
    except Exception as e:
        await logs_bot("error", f"Ошибка получения статистики: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 