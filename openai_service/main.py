import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

from fastapi import FastAPI
from app.core.logging import logs_bot
from app.db.database import init_db
from app.api.v1.router import api_router

app = FastAPI()

# Подключаем роутер API v1
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    try:
        await init_db()  # Инициализация базы данных
        await logs_bot("info", "Сервис успешно запущен")  # Логируем успешный запуск сервиса
    except Exception as e:
        await logs_bot("error", f"Не удалось запустить сервис: {str(e)}")  # Логируем ошибку при запуске
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",  # Запуск приложения FastAPI
        host="0.0.0.0",  # Указываем хост
        port=8000,  # Указываем порт
        reload=True,  # Включаем режим перезагрузки
        log_level="info"  # Уровень логирования
    )
