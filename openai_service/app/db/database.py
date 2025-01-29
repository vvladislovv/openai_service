from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON, UUID, select, Text, func
from .models import User, ChatHistory, ContextSession, JsonData
from typing import Any, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
import os
import json

load_dotenv()

POSTGRES_URL: str = os.getenv("DATABASE_URL")

engine = create_async_engine(POSTGRES_URL, echo=True)
AsyncSessionLocal: sessionmaker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

# Функция для создания таблиц
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Сначала удаляем все таблицы
        await conn.run_sync(Base.metadata.create_all)  # Затем создаем заново

# Функция для получения сессии базы данных
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def add_to_table(table_class: Base, data: dict) -> Any:
    """
    Общая функция для добавления данных в любую таблицу с проверкой user_id
    
    Аргументы:
        table_class: Base - Класс модели SQLAlchemy
        data: dict - Данные для вставки
        
    Возвращает:
        Созданную или существующую запись
    """
    async with AsyncSessionLocal() as session:
        if 'user_id' in data:
            # Проверяем, существует ли запись с этим user_id
            existing = await session.execute(
                select(table_class).where(
                    table_class.user_id == data['user_id']
                )
            )
            existing_record: Optional[Base] = existing.scalar_one_or_none()
            
            if existing_record:
                # Обновляем существующую запись
                for key, value in data.items():
                    setattr(existing_record, key, value)
                await session.commit()
                return existing_record
                
        # Создаем новую запись
        new_record: Base = table_class(**data)
        session.add(new_record)
        await session.commit()
        await session.refresh(new_record)
        return new_record
    
async def add_info_to_database(table_class: Base, data: dict) -> Any:
    """
    Функция для добавления информации в базу данных.
    
    Аргументы:
        table_class: Base - Класс модели SQLAlchemy
        data: dict - Данные для вставки
        
    Возвращает:
        Созданную или существующую запись
    """
    async with AsyncSessionLocal() as session:
        # Проверяем, существует ли запись с указанным user_id
        if 'user_id' in data:
            existing = await session.execute(
                select(table_class).where(
                    table_class.user_id == data['user_id']
                )
            )
            existing_record: Optional[Base] = existing.scalar_one_or_none()
            
            if existing_record:
                # Обновляем существующую запись
                for key, value in data.items():
                    setattr(existing_record, key, value)
                await session.commit()
                return existing_record
                
        # Создаем новую запись
        new_record: Base = table_class(**data)
        session.add(new_record)
        await session.commit()
        await session.refresh(new_record)
        return new_record


async def get_table_data(table_class: Base) -> List[dict]:
    """
    Функция для получения данных из указанной таблицы в формате JSON.
    
    Аргументы:
        table_class: Base - Класс модели SQLAlchemy
        
    Возвращает:
        Список словарей с данными из таблицы
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(table_class))
        records: List[Base] = result.scalars().all()
        return [record.__dict__ for record in records]

async def save_chat_history(request: Any, response: Any) -> None:
    """
    Сохраняет историю чата в базу данных.
    
    Аргументы:
        request: Объект запроса с данными чата
        response: Объект ответа от модели
        
    Возвращает:
        None
    """
    async with AsyncSessionLocal() as session:
        history: ChatHistory = ChatHistory(
            id=response.id,
            model=request.model,
            request=json.dumps([m.dict() for m in request.messages]),
            response=response.response,
            tokens_used=response.tokens_used,
            session_id=getattr(request, 'session_id', None)
        )
        session.add(history)
        await session.commit()

async def get_history(model: Optional[str], start_date: Optional[datetime], end_date: Optional[datetime], page: int, page_size: int) -> Tuple[List[ChatHistory], int]:
    """
    Получает историю чатов с возможностью фильтрации и пагинации.
    
    Аргументы:
        model: str - Фильтр по модели (опционально)
        start_date: datetime - Начальная дата фильтрации (опционально)
        end_date: datetime - Конечная дата фильтрации (опционально)
        page: int - Номер страницы
        page_size: int - Количество записей на странице
        
    Возвращает:
        Tuple[List[ChatHistory], int] - Список записей истории и общее количество
    """
    async with AsyncSessionLocal() as session:
        query = select(ChatHistory)
        
        if model:
            query = query.where(ChatHistory.model == model)
        if start_date:
            query = query.where(ChatHistory.created_at >= start_date)
        if end_date:
            query = query.where(ChatHistory.created_at <= end_date)
        
        # Получаем общее количество записей
        total: int = await session.scalar(select(func.count()).select_from(query.subquery()))
        
        # Применяем пагинацию
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(query)
        history: List[ChatHistory] = result.scalars().all()
        
        return history, total

async def get_statistics() -> dict:
    """
    Получает статистику использования чата.
    
    Возвращает:
        dict - Словарь со статистикой:
            - total_requests: Общее количество запросов
            - requests_by_model: Количество запросов по каждой модели
            - total_tokens: Общее количество использованных токенов
    """
    async with AsyncSessionLocal() as session:
        # Получаем общее количество запросов
        total_requests: int = await session.scalar(
            select(func.count()).select_from(ChatHistory)
        )
        
        # Получаем статистику по моделям
        models_query = select(
            ChatHistory.model,
            func.count(ChatHistory.id).label('count')
        ).group_by(ChatHistory.model)
        
        models_result = await session.execute(models_query)
        models_stats: dict = {row.model: row.count for row in models_result}
        
        # Получаем общее количество токенов
        total_tokens: int = await session.scalar(
            select(func.sum(ChatHistory.tokens_used))
        ) or 0
        
        return {
            "total_requests": total_requests,
            "requests_by_model": models_stats,
            "total_tokens": total_tokens
        }
