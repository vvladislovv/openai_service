import openai
from datetime import datetime
from app.models.chat import ChatRequest, ChatResponse, ChatWithContextRequest
from app.core.logging import logs_bot
from app.db.database import save_chat_history
import os

class OpenAIService:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.sessions = {}

    async def create_chat_completion(self, request: ChatRequest) -> ChatResponse:
        """
        Создает завершение чата, отправляя запрос к API OpenAI.

        Аргументы:
            request (ChatRequest): Запрос на создание завершения чата, содержащий модель и сообщения.

        Возвращает:
            ChatResponse: Ответ от API OpenAI, содержащий идентификатор, модель, время создания, ответ и количество использованных токенов.
        """
        try:
            start_time = datetime.now()
            response = await openai.ChatCompletion.acreate(
                model=request.model,
                messages=[{"role": m.role, "content": m.content} for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            chat_response = ChatResponse(
                id=response.id,
                model=request.model,
                created=int(start_time.timestamp()),
                response=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens
            )

            await save_chat_history(request, chat_response)
            return chat_response

        except Exception as e:
            await logs_bot("error", f"Ошибка API OpenAI: {str(e)}")
            raise

    async def chat_with_context(self, request: ChatWithContextRequest) -> ChatResponse:
        """
        Обрабатывает чат с контекстом, сохраняя сообщения в сессии.

        Аргументы:
            request (ChatWithContextRequest): Запрос на чат с контекстом, содержащий идентификатор сессии и сообщения.

        Возвращает:
            ChatResponse: Ответ от API OpenAI, содержащий завершение чата с учетом контекста.
        """
        if request.session_id not in self.sessions:
            self.sessions[request.session_id] = []

        self.sessions[request.session_id].extend(request.messages)
        request.messages = self.sessions[request.session_id]
        
        return await self.create_chat_completion(request) 