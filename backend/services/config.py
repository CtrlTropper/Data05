"""
Configuration settings
Cấu hình cho hệ thống
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "RAG + LLM Chatbot"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Model paths
    EMBEDDING_MODEL_PATH: str = "models/multilingual-e5-large"
    LLM_MODEL_PATH: str = "models/gpt-oss-20b"
    
    # Database settings
    FAISS_INDEX_PATH: str = "data/faiss_index"
    METADATA_DB_PATH: str = "data/metadata"
    
    # Upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt", ".md"]
    
    # Processing settings
    DEFAULT_CHUNK_SIZE: int = 500
    DEFAULT_CHUNK_OVERLAP: int = 50
    DEFAULT_TOP_K: int = 5
    
    # LLM settings
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
