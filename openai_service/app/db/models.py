from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON, UUID, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone, timedelta
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    api_key = Column(String(100))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(UUID(as_uuid=True), nullable=False)  
    chat_name = Column(String)
    question = Column(Text)
    answer = Column(Text)
    model_gpt = Column(String)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now().replace(second=0, microsecond=0), nullable=False)
    context = Column(JSON)
    token = Column(Integer)

class ContextSession(Base):
    __tablename__ = "context_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(UUID)
    context = Column(JSON)
    context_length = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now().replace(second=0, microsecond=0), nullable=False)
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now().replace(second=0, microsecond=0), nullable=False)
    last_message_at = Column(TIMESTAMP)

class JsonData(Base):
    __tablename__ = "json_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now().replace(second=0, microsecond=0), nullable=False)
    data = Column(JSON)

