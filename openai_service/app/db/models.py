from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON, UUID, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    api_key = Column(String(100))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(String, primary_key=True)
    model = Column(String)
    request = Column(Text)
    response = Column(Text)
    tokens_used = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    session_id = Column(String, nullable=True)

class ContextSession(Base):
    __tablename__ = "context_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(UUID)
    context = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class JsonData(Base):
    __tablename__ = "json_data"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    data = Column(JSON)
