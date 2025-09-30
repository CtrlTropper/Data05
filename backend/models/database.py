"""
Database models
Định nghĩa các model cho database
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Document(Base):
    """Model cho document"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    processed_time = Column(DateTime, nullable=True)
    chunks_count = Column(Integer, default=0)
    status = Column(String, default="uploaded")  # uploaded, processing, processed, error
    
    # Relationships
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="document")

class Chunk(Base):
    """Model cho chunk"""
    __tablename__ = "chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    start_pos = Column(Integer, nullable=True)
    end_pos = Column(Integer, nullable=True)
    embedding_id = Column(String, nullable=True)  # ID trong FAISS index
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")

class ChatSession(Base):
    """Model cho chat session"""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)  # None = global chat
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    message_count = Column(Integer, default=0)
    
    # Relationships
    document = relationship("Document", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """Model cho chat message"""
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer, nullable=True)
    processing_time = Column(Float, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class SystemConfig(Base):
    """Model cho system configuration"""
    __tablename__ = "system_config"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ModelStatus(Base):
    """Model cho trạng thái AI models"""
    __tablename__ = "model_status"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # embedding, llm
    loaded = Column(Boolean, default=False)
    load_time = Column(DateTime, nullable=True)
    memory_usage = Column(Float, nullable=True)  # MB
    device = Column(String, nullable=True)  # cpu, cuda
    last_used = Column(DateTime, nullable=True)
