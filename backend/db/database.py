"""
Database connection và session management
Quản lý kết nối database SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os
from pathlib import Path

from models.database import Base

# Database configuration
DATABASE_URL = "sqlite:///./data/chatbot.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    poolclass=StaticPool,
    echo=False  # Set to True for SQL logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Tạo tất cả tables"""
    try:
        # Create data directory
        Path("data").mkdir(exist_ok=True)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise

def get_db() -> Generator[Session, None, None]:
    """
    Dependency để lấy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Khởi tạo database"""
    try:
        create_tables()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
