from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from typing import Optional
import os

API_KEY_NAME = os.getenv("API_KEY_NAME", "X-API-Key")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: Optional[str] = Security(api_key_header)) -> str:
    if api_key_header is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="API key is missing"
        )
    
    # Получаем API ключ из переменных окружения
    api_key = os.getenv("API_KEY")
    if api_key is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="API key is not configured on server"
        )
    
    if api_key_header != api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Invalid API key"
        )
        
    return api_key_header
