from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON, UUID, select, Text, func
from .models import Base, User, ChatHistory, ContextSession, JsonData
from typing import Any, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import uuid

load_dotenv()

POSTGRES_URL: str = os.getenv("DATABASE_URL")

engine = create_async_engine(POSTGRES_URL, echo=True)
AsyncSessionLocal: sessionmaker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Функция для создания таблиц
async def init_db() -> None:
    """
    Инициализирует базу данных, создавая все необходимые таблицы.
    Импортирует все модели перед созданием таблиц.
    
    Возвращает:
        None
    """
    async with engine.begin() as conn:
        # Импортируем все модели перед созданием таблиц
        from .models import Base, User, ChatHistory, ContextSession, JsonData
        await conn.run_sync(Base.metadata.create_all)

# Функция для получения сессии базы данных
async def get_db() -> AsyncSession:
    """
    Создает и возвращает асинхронную сессию базы данных.
    Использует контекстный менеджер для автоматического закрытия сессии.
    
    Возвращает:
        AsyncSession: Асинхронная сессия SQLAlchemy для работы с базой данных
        
    Yields:
        AsyncSession: Сессия базы данных
    """
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
        Созданную или существующую запись или False, если не удалось вставить данные
    """
    
    async with AsyncSessionLocal() as session:
        if 'chat_id' in data:
            # Проверяем, существует ли запись с этим chat_id
            existing = await session.execute(
                select(table_class).where(
                    table_class.chat_id == data['chat_id']
                )
            )

            existing_record: Optional[Base] = existing.scalar_one_or_none()
            
            if existing_record:
                # Обновляем существующую запись
                for key, value in data.items():
                    setattr(existing_record, key, value)
                await session.commit()
                return existing_record
        
        # Проверяем, можно ли создать новую запись
        try:
            new_record: Base = table_class(**data)
            session.add(new_record)
            await session.commit()
            await session.refresh(new_record)
            return new_record
        except Exception as e:
            # Если не удалось вставить данные, возвращаем False
            return False

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

async def save_chat_history(request: Any = None) -> ChatHistory:
    """
    Сохраняет историю чата в базу данных.
    
    Аргументы:
        request: Объект запроса с данными чата
        response: Объект ответа от модели
        
    Возвращает:
        ChatHistory - Созданная запись истории чата
    """

    async with AsyncSessionLocal() as session:
        # Создаем словарь с данными для истории
        history_data = {
            'chat_name': request['chat_name'],
            'model_gpt': request['model_gpt'],
            'question': request['question'],  # Прямо используем запрос пользователя
            'answer': "",  # Используем переданный ответ
            'token': request['token'],  # Используем переданное количество токенов
            'context': request['context'],  # Используем переданный контекст
            'created_at': request.get('created_at', datetime.utcnow())  # Используем переданное время или текущее
        }
        
        # Добавляем chat_id только если его нет в request
        if 'chat_id' not in request:
            history_data['chat_id'] = uuid.uuid4()
        else:
            history_data['chat_id'] = request['chat_id']

        history = ChatHistory(**history_data)
        session.add(history)
        await session.commit()
        await session.refresh(history)
        return history



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

async def delete_table(table_class: Base, chat_id: str) -> bool:
    """
    Удаляет чат из базы данных по его идентификатору.
    
    Аргументы:
        chat_id: str - Уникальный идентификатор чата для удаления
        table_class: Base - Класс модели SQLAlchemy для удаления
        
    Возвращает:
        bool: True если чат был успешно удален, False если чат не найден
    """
    async with AsyncSessionLocal() as session:
        try:
            # Находим чат по ID
            chat = await session.scalar(
                select(table_class).where(table_class.chat_id == chat_id)
            )
            if chat is None:
                return False  # Чат не найден
            
            # Удаляем чат
            await session.delete(chat)
            await session.commit()
            return True  # Успешно удалено

        except Exception as e:
            print(f"Error occurred while deleting chat: {e}")
            return False  # Возвращаем False в случае ошибки

async def get_chat_data(chat_id: str) -> dict:
    """
    Получает данные чата по идентификатору.

    Параметры:
        chat_id: str - Идентификатор чата

    Возвращает:
        dict: Данные чата, если найден, иначе None
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ChatHistory).where(ChatHistory.chat_id == chat_id))
        chat_data = result.scalars().first()
        
        if chat_data:
            return {
                "model_gpt": chat_data.model_gpt,
                "context": chat_data.context,
                # Добавьте другие необходимые поля
            }
    return None
