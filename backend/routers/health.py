"""
Health check router
Router kiểm tra trạng thái hệ thống
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class HealthResponse(BaseModel):
    """Response model cho health check"""
    status: str
    message: str
    timestamp: str
    version: str

@router.get("/health", response_model=HealthResponse)
async def health_check() -> Dict[str, Any]:
    """
    Kiểm tra trạng thái hệ thống
    Returns:
        Dict: Thông tin trạng thái hệ thống
    """
    from datetime import datetime
    
    return {
        "status": "ok",
        "message": "RAG + LLM Chatbot API is running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """
    Kiểm tra chi tiết trạng thái các component
    """
    # TODO: Implement detailed health checks
    # - Model loading status
    # - Database connection
    # - Memory usage
    # - Disk space
    pass
