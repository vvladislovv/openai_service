from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse, ChatWithContextRequest
from app.services.openai import OpenAIService
from app.core.logging import logs_bot

router = APIRouter()
openai_service = OpenAIService()

@router.post("/completions", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Обрабатывает запрос на завершение чата.

    Эта функция принимает запрос на завершение чата и вызывает метод
    `create_chat_completion` сервиса OpenAI для получения ответа. 
    Если запрос успешен, возвращается ответ. В случае ошибки 
    функция записывает сообщение об ошибке и вызывает исключение HTTP 500.
    
    Параметры:
        request (ChatRequest): Запрос на завершение чата.

    Возвращает:
        ChatResponse: Ответ на запрос завершения чата.
    """
    try:
        response = await openai_service.create_chat_completion(request)
        return response
    except Exception as e:
        await logs_bot("error", f"Ошибка завершения чата: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/with-context", response_model=ChatResponse)
async def chat_with_context(request: ChatWithContextRequest):
    """
    Обрабатывает запрос на завершение чата с контекстом.

    Эта функция принимает запрос на завершение чата с контекстом и 
    вызывает метод `chat_with_context` сервиса OpenAI для получения ответа. 
    Если запрос успешен, возвращается ответ. В случае ошибки 
    функция записывает сообщение об ошибке и вызывает исключение HTTP 500.
    
    Параметры:
        request (ChatWithContextRequest): Запрос на завершение чата с контекстом.

    Возвращает:
        ChatResponse: Ответ на запрос завершения чата с контекстом.
    """
    try:
        response = await openai_service.chat_with_context(request)
        return response
    except Exception as e:
        await logs_bot("error", f"Ошибка завершения чата с контекстом: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
