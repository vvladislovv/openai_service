from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from app.models.history import HistoryResponse
from app.db.database import get_history
from app.core.logging import logs_bot

router = APIRouter()
@router.get("", response_model=List[HistoryResponse])
async def get_chat_history(
    model: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """
    Получает историю чата на основе заданных параметров.

    Эта функция извлекает историю чата из базы данных, используя параметры
    фильтрации, такие как модель, дата начала и дата окончания. Она также
    поддерживает пагинацию через параметры страницы и размера страницы.

    Параметры:
        model (Optional[str]): Модель, по которой будет фильтроваться история.
        start_date (Optional[datetime]): Дата начала для фильтрации истории.
        end_date (Optional[datetime]): Дата окончания для фильтрации истории.
        page (int): Номер страницы для пагинации (по умолчанию 1).
        page_size (int): Количество записей на странице (по умолчанию 10, максимум 100).

    Возвращает:
        List[HistoryResponse]: Список объектов истории чата.
    """
    try:
        history, total = await get_history(model, start_date, end_date, page, page_size)
        return history
    except Exception as e:
        await logs_bot("error", f"Ошибка получения истории: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
