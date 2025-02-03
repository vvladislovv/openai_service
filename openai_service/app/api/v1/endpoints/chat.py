from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.db.database import ChatHistory, delete_table, save_chat_history, add_to_table, get_chat_data
from app.models.chat import ChatCreate, ChatRename, ChatCompletion, ChatRequest
from app.services.openai import OpenAIService

router = APIRouter()
openai_service = OpenAIService()


"""
curl -X POST http://localhost:8000/api/v1/chat/create \
-H "Content-Type: application/json" \
-H "X-API-Key: asdfa33945asdf2awfasdfaw" \
-d '{
    "chat_name": "tester_Tsa",
    "question": "Как дела?",
    "model_gpt": "gpt-3.5-turbo",
    "answer": "{}",
    "context": "{}",
    "token": 0
}'
"""

"""
curl -X PUT http://localhost:8000/api/v1/chat/rename \
-H "Content-Type: application/json" \
-H "X-API-Key: asdfa33945asdf2awfasdfaw" \
-d '{
    "chat_id": "5205f8e1-c4c5-4592-8c46-550b9b218f14", 
    "new_name": "Новое название чата 1"
}'
"""

'''
curl -X DELETE http://localhost:8000/api/v1/chat/delete/"5205f8e1-c4c5-4592-8c46-550b9b218f14" \
-H "Content-Type: application/json" \
-H "X-API-Key: asdfa33945asdf2awfasdfaw"
'''

"""
    curl -X POST 'http://localhost:8000/api/v1/chat/completions' \
    -H 'Content-Type: application/json' \
    -H 'X-API-Key: asdfa33945asdf2awfasdfaw' \
    -d '{
        "chat_id": "11bc9119-4c13-4144-8c20-16a24aa2c833",
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "2+2=?!"}]
    }'
"""

@router.post("/create")
async def create_chat(chat: ChatCreate):
    """
    Создает новый чат и сохраняет его в базе данных.
    
    Параметры:
        chat: ChatCreate - Модель с данными чата:
            - chat_name: название чата
            - question: вопрос пользователя 
            - model_gpt: используемая GPT модель
            - answer: ответ модели
            - context: контекст беседы
            - token: количество использованных токенов
    
    Возвращает:
        dict: Словарь с идентификатором созданного чата:
            - chat_id: идентификатор чата (название чата)
    """

    chat_data = {
        "chat_name": chat.chat_name,
        "question": chat.question,
        "model_gpt": chat.model_gpt,
        "created_at": datetime.utcnow(),  # Записываем текущее время
        "context": chat.context, 
        "token": chat.token,
        "answer": chat.answer
    }

    await save_chat_history(chat_data) 
    return {"chat_id": chat_data["chat_name"]}

@router.delete("/delete/{chat_id}")
async def delete_chat_endpoint(chat_id: str):
    """
    Удаляет указанный чат из базы данных.
    
    Параметры:
        chat_id: str - Уникальный идентификатор чата для удаления
    
    Возвращает:
        dict: Статус выполнения операции:
            - status: статус операции
            - message: сообщение о результате
        
    Вызывает:
        HTTPException: Если чат не найден (404)
    """

    # Вызываем функцию удаления чата
    success = await delete_table(ChatHistory, chat_id)
    
    # Если чат не найден, выбрасываем исключение
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    return {"status": "success", "message": "Chat successfully deleted"}

@router.put("/rename")
async def rename_chat(chat: ChatRename):
    """
    Обновляет название существующего чата в базе данных.
    
    Параметры:
        chat: ChatRename - Модель с данными для переименования:
            - chat_id: идентификатор чата
            - new_name: новое название чата
    
    Возвращает:
        dict: Информация об обновленном чате:
            - chat_id: идентификатор чата
            - new_name: новое название чата
            
    Вызывает:
        HTTPException: Если чат не найден (404)
    """

    
    # Обновляем данные чата
    chat_data = {
        "chat_id": chat.chat_id,
        "chat_name": chat.new_name,
    }
    
    success = await add_to_table(ChatHistory, chat_data)  # Используем функцию для обновления данных

    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return {"chat_id": chat.chat_id, "new_name": chat.new_name}

@router.post("/completions", response_model=dict)
async def generate_completion(completion: ChatCompletion):
    """
    Генерирует ответ с помощью OpenAI API и сохраняет его в истории чата.
    
    Параметры:
        completion: ChatCompletion - Модель с данными для генерации:
            - chat_id: идентификатор чата
            - model: модель GPT для использования
            - messages: список сообщений для контекста (опционально)
            - image_url: URL изображения (опционально)
            - audio_file: путь к аудиофайлу (опционально)
    
    Возвращает:
        dict: Сгенерированный ответ:
            - chat_id: идентификатор чата
            - response: текст ответа от модели или результат обработки изображения/аудио
            
    Вызывает:
        HTTPException: 
            - 500: При ошибке получения ответа от OpenAI
            - 404: При ошибке сохранения истории чата
            - 500: При других ошибках
    """
    try:
        if completion.messages:
            # Обработка текстовых сообщений
            chat_request = ChatRequest(
                chat_id=completion.chat_id,
                model=completion.model,
                messages=completion.messages
            )
            response_text = await openai_service.create_chat_completion(chat_request)

        elif completion.image_url:
            # Обработка изображений
            response_text = await openai_service.process_image(completion.image_url)

        elif completion.audio_file:
            # Обработка аудио
            response_text = await openai_service.process_audio(completion.audio_file)

        else:
            raise HTTPException(status_code=400, detail="No valid input provided")

        if response_text is None or response_text == "Error occurred":
            raise HTTPException(status_code=500, detail="Failed to get response from OpenAI")

        # Сохраняем историю чата
        chat_history_data = {
            "chat_id": completion.chat_id,
            "answer": response_text,
        }

        success = await add_to_table(ChatHistory, chat_history_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="Failed to save chat history")
        
        return {
            "chat_id": completion.chat_id,
            "response": response_text,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
