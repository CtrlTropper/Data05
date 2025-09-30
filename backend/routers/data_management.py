"""
Data Management Router
Quản lý dữ liệu ban đầu và categories
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from services.data_initialization import data_initialization_service

logger = logging.getLogger(__name__)
router = APIRouter()

class CategoryStatsResponse(BaseModel):
    """Response model cho category stats"""
    categories: Dict[str, Dict[str, Any]]
    total_documents: int
    total_categories: int

class ReloadCategoryRequest(BaseModel):
    """Request model cho reload category"""
    category: str

class ReloadCategoryResponse(BaseModel):
    """Response model cho reload category"""
    success: bool
    category: str
    documents_processed: int
    chunks_created: int
    error: Optional[str] = None

@router.get("/data/categories/stats", response_model=CategoryStatsResponse)
async def get_category_stats():
    """
    Lấy thống kê về các category dữ liệu
    """
    try:
        stats = await data_initialization_service.get_category_stats()
        
        total_documents = sum(cat.get("document_count", 0) for cat in stats.values())
        total_categories = len([cat for cat in stats.values() if cat.get("exists", False)])
        
        return CategoryStatsResponse(
            categories=stats,
            total_documents=total_documents,
            total_categories=total_categories
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting category stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy thống kê category: {str(e)}"
        )

@router.post("/data/categories/reload", response_model=ReloadCategoryResponse)
async def reload_category(request: ReloadCategoryRequest):
    """
    Reload một category cụ thể
    """
    try:
        result = await data_initialization_service.reload_category(request.category)
        
        if result.get("success"):
            return ReloadCategoryResponse(
                success=True,
                category=result["category"],
                documents_processed=result["documents_processed"],
                chunks_created=result["chunks_created"]
            )
        else:
            return ReloadCategoryResponse(
                success=False,
                category=request.category,
                documents_processed=0,
                chunks_created=0,
                error=result.get("error", "Unknown error")
            )
            
    except Exception as e:
        logger.error(f"❌ Error reloading category: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi reload category: {str(e)}"
        )

@router.get("/data/categories")
async def list_categories():
    """
    Liệt kê tất cả categories có sẵn
    """
    try:
        categories = [
            {
                "name": "Luat",
                "description": "Tài liệu về Luật An toàn thông tin Việt Nam",
                "path": "data/Luat"
            },
            {
                "name": "TaiLieuTiengViet", 
                "description": "Tài liệu An toàn thông tin bằng tiếng Việt",
                "path": "data/TaiLieuTiengViet"
            },
            {
                "name": "TaiLieuTiengAnh",
                "description": "Tài liệu An toàn thông tin bằng tiếng Anh", 
                "path": "data/TaiLieuTiengAnh"
            },
            {
                "name": "Uploads",
                "description": "Tài liệu do người dùng upload",
                "path": "data/uploads"
            }
        ]
        
        return {
            "categories": categories,
            "total": len(categories)
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing categories: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi liệt kê categories: {str(e)}"
        )

@router.get("/data/status")
async def get_data_status():
    """
    Lấy trạng thái tổng quan của dữ liệu
    """
    try:
        # Get category stats
        stats = await data_initialization_service.get_category_stats()
        
        # Get vector store stats
        from db.faiss_store import faiss_store
        vector_stats = faiss_store.get_stats()
        
        # Calculate totals
        total_documents = sum(cat.get("document_count", 0) for cat in stats.values())
        total_categories = len([cat for cat in stats.values() if cat.get("exists", False)])
        
        return {
            "data_initialization": {
                "initialized": data_initialization_service.is_initialized,
                "total_documents": total_documents,
                "total_categories": total_categories,
                "categories": stats
            },
            "vector_store": vector_stats,
            "system_status": "ready" if data_initialization_service.is_initialized else "initializing"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting data status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy trạng thái dữ liệu: {str(e)}"
        )
