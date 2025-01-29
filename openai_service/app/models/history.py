from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class HistoryResponse(BaseModel):
    id: str
    model: str
    request: str
    response: str
    tokens_used: int
    created_at: datetime
    session_id: Optional[str] = None

class StatisticsResponse(BaseModel):
    total_requests: int
    requests_by_model: dict
    total_tokens: int
    average_response_time: float 