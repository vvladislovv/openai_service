from openai import AsyncOpenAI
from app.models.chat import ChatRequest, ChatResponse, ChatWithContextRequest
from app.core.logging import logs_bot
import os

class OpenAIService:
    def __init__(self):
        self.sessions = {}
        self.proxy_api_url = os.getenv("PROXY_API_URL")
        self.proxy_api_key = os.getenv("PROXY_API_KEY")
        self.client = AsyncOpenAI(
            api_key=self.proxy_api_key,
            base_url=self.proxy_api_url
        )

    async def create_chat_completion(self, request: ChatRequest) -> str:
        """
        Функция для создания завершения чата, отправляя запрос через ProxyAPI.
        
        Аргументы:
            request: ChatRequest - Объект с данными для завершения чата, 
                      содержащий модель и сообщения.
        
        Возвращает:
            str: Текст ответа от OpenAI API или сообщение об ошибке.
        
        Описание:
            Эта функция создает завершение чата, отправляя запрос через ProxyAPI. 
            Она принимает запрос от пользователя, содержащий модель и сообщения, 
            отправляет запрос на OpenAI API, ожидает ответ и возвращает текст ответа.
            
            Если ответ от OpenAI API пустой, функция возвращает сообщение об ошибке.
            Если во время выполнения функции возникает исключение, функция логгирует ошибку 
            и возвращает сообщение об ошибке.
        """
        try:
            # Отправляем запрос на завершение чата
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=request.messages
            )
            
            # Проверяем, получен ли ответ от OpenAI API
            if not response or not response.choices:
                await logs_bot("error", "Empty response from OpenAI API")
                return "No response received"
                
            # Возвращаем текст ответа
            return response.choices[0].message.content
            
        except Exception as e:
            await logs_bot("error", f"Error in create_chat_completion: {str(e)}")
            return f"Error occurred: {str(e)}"

    async def process_image(self, image_url: str) -> str:
        """
        Обрабатывает изображение с помощью OpenAI API.
        
        Аргументы:
            image_url: URL изображения для обработки.
        
        Возвращает:
            str: Ответ от OpenAI API о содержимом изображения или сообщение об ошибке.
        
        Описание:
            Эта функция отправляет запрос на OpenAI API для анализа изображения по указанному URL.
            Она ожидает ответ и возвращает текстовое описание содержимого изображения.
            Если ответ пустой или возникает ошибка, функция логгирует ошибку и возвращает сообщение об ошибке.
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What's in this image?"},
                            {"type": "image_url", "image_url": image_url}
                        ]
                    }
                ]
            )

            if not response or not response.choices:
                await logs_bot("error", "Empty response from OpenAI Vision API")
                return "No response received"

            return response.choices[0].message.content

        except Exception as e:
            await logs_bot("error", f"Error in process_image: {str(e)}")
            return f"Error occurred: {str(e)}"

    async def process_audio(self, audio_file: str) -> str:
        """
        Обрабатывает аудиофайл с помощью OpenAI API.
        
        Параметры:
            audio_file: путь к аудиофайлу для транскрипции.
        
        Возвращает:
            str: Результат транскрипции аудиофайла или сообщение об ошибке.
        
        Описание:
            Эта функция отправляет аудиофайл на OpenAI API для транскрипции.
            Она ожидает текстовый ответ и возвращает его. Если возникает ошибка, 
            функция логгирует ошибку и возвращает сообщение об ошибке.
        """
        try:
            with open(audio_file, "rb") as audio:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )

            return transcript

        except Exception as e:
            await logs_bot("error", f"Error in process_audio: {str(e)}")
            return f"Error occurred: {str(e)}"

    async def chat_with_context(self, request: ChatWithContextRequest) -> ChatResponse:
        """
        Обрабатывает чат с контекстом, сохраняя сообщения в сессии.
        
        Параметры:
            request: ChatWithContextRequest - Запрос, содержащий идентификатор сессии и сообщения чата.
        
        Возвращает:
            ChatResponse: Ответ на чат с учетом контекста.
        
        Описание:
            Эта функция сохраняет сообщения чата в сессии, чтобы учитывать контекст 
            при создании ответа. Если сессия не существует, она создается. 
            Затем функция вызывает метод для создания завершения чата с учетом контекста.
        """
        if request.session_id not in self.sessions:
            self.sessions[request.session_id] = []

        self.sessions[request.session_id].extend(request.messages)
        request.messages = self.sessions[request.session_id]

        return await self.create_chat_completion(request)

    async def transcribe_audio(self, audio_file: str) -> str:
        """
        Транскрибирует аудиофайл в текст с использованием OpenAI API.
        
        Параметры:
            audio_file: путь к аудиофайлу для транскрипции.
        
        Возвращает:
            str: Результат транскрипции аудиофайла или сообщение об ошибке.
        
        Описание:
            Эта функция отправляет аудиофайл на OpenAI API для транскрипции и 
            возвращает текстовый результат. Если возникает ошибка, функция логгирует 
            ошибку и возвращает сообщение об ошибке.
        """
        try:
            with open(audio_file, "rb") as audio:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )

            return transcript

        except Exception as e:
            await logs_bot("error", f"Error in transcribe_audio: {str(e)}")
            return f"Error occurred: {str(e)}"

    async def generate_image(self, prompt: str, size: str) -> str:
        """
        Генерирует изображение по описанию с использованием OpenAI API.
        
        Параметры:
            prompt: описание для генерации изображения.
            size: размер изображения.
        
        Возвращает:
            str: URL сгенерированного изображения или сообщение об ошибке.
        
        Описание:
            Эта функция отправляет запрос на OpenAI API для генерации изображения 
            на основе заданного описания и размера. Она возвращает URL сгенерированного 
            изображения или сообщение об ошибке, если что-то пошло не так.
        """
        try:
            response = await self.client.images.create(
                prompt=prompt,
                n=1,
                size=size
            )

            if not response or not response.data:
                await logs_bot("error", "Empty response from OpenAI Image API")
                return "No response received"

            return response.data[0].url

        except Exception as e:
            await logs_bot("error", f"Error in generate_image: {str(e)}")
            return f"Error occurred: {str(e)}"