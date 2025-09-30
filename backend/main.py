"""
Main FastAPI application for RAG + LLM Chatbot System
Hệ thống chatbot RAG + LLM hoạt động offline
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from pathlib import Path

# Import routers
from routers import health, documents, chat, embedding, search, chat_sessions, data_management

# Import services
from services.model_manager import ModelManager
from services.config import Settings
from services.embedding_service import embedding_service
from services.llm_service import llm_service
from services.chat_session_service import chat_session_service
from services.rag_service import rag_service
from services.pdf_processor import pdf_processor
from services.data_initialization import data_initialization_service
from services.vector_service import vector_service
from db.faiss_store import faiss_store

# Initialize FastAPI app
app = FastAPI(
    title="RAG + LLM Chatbot API",
    description="API cho hệ thống chatbot RAG + LLM hoạt động offline",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global settings
settings = Settings()

# Global model manager
model_manager = ModelManager()

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(embedding.router, prefix="/api", tags=["Embedding"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(chat_sessions.router, prefix="/api", tags=["Chat Sessions"])
app.include_router(data_management.router, prefix="/api", tags=["Data Management"])

@app.on_event("startup")
async def startup_event():
    """Khởi tạo các service khi start app"""
    print("🚀 Starting RAG + LLM Chatbot API...")
    
    # Tạo các thư mục cần thiết
    os.makedirs("data/faiss_index", exist_ok=True)
    os.makedirs("data/faiss_store", exist_ok=True)
    os.makedirs("data/metadata", exist_ok=True)
    os.makedirs("data/docs", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("models/embedding", exist_ok=True)
    os.makedirs("models/llm", exist_ok=True)
    
    # Khởi tạo model manager
    await model_manager.initialize()
    
    # Khởi tạo embedding service
    await embedding_service.load_model()
    
        # Khởi tạo LLM service
        await llm_service.load_model()

        # Khởi tạo chat session service
        await chat_session_service.initialize()

        # Khởi tạo RAG service với dependencies
        rag_service.chat_session_service = chat_session_service

        # Khởi tạo PDF processor
        await pdf_processor.initialize()

        # Khởi tạo data initialization service
        await data_initialization_service.initialize(
            embedding_service=embedding_service,
            vector_service=vector_service,
            pdf_processor=pdf_processor
        )

        print("✅ API started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup khi shutdown app"""
    print("🛑 Shutting down RAG + LLM Chatbot API...")
    await model_manager.cleanup()
    await embedding_service.cleanup()
    await llm_service.cleanup()
    await chat_session_service.cleanup()
    print("✅ API shutdown complete!")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "Something went wrong"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
