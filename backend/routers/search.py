"""
Search Router
API tìm kiếm vector và context
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import numpy as np

# Import services
from services.embedding_service import embedding_service
from db.faiss_store import faiss_store

logger = logging.getLogger(__name__)

router = APIRouter()

class SearchRequest(BaseModel):
    """Request model cho search"""
    query: str
    top_k: int = 5
    doc_id: Optional[str] = None

class SearchResponse(BaseModel):
    """Response model cho search"""
    query: str
    results: List[Dict[str, Any]]
    total_found: int
    search_time: float

class VectorSearchRequest(BaseModel):
    """Request model cho vector search"""
    vector: List[float]
    top_k: int = 5
    doc_id: Optional[str] = None

@router.post("/search/text", response_model=SearchResponse)
async def search_text(request: SearchRequest) -> SearchResponse:
    """
    Tìm kiếm bằng text query
    """
    try:
        import time
        start_time = time.time()
        
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query không được để trống"
            )
        
        # Search using FAISS store
        results = faiss_store.search_text(
            query_text=request.query.strip(),
            top_k=request.top_k,
            doc_id=request.doc_id,
            embedding_service=embedding_service
        )
        
        search_time = time.time() - start_time
        
        logger.info(f"✅ Text search completed: {len(results)} results in {search_time:.3f}s")
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_found=len(results),
            search_time=search_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in text search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tìm kiếm: {str(e)}"
        )

@router.post("/search/vector", response_model=SearchResponse)
async def search_vector(request: VectorSearchRequest) -> SearchResponse:
    """
    Tìm kiếm bằng vector
    """
    try:
        import time
        start_time = time.time()
        
        if not request.vector:
            raise HTTPException(
                status_code=400,
                detail="Vector không được để trống"
            )
        
        # Convert to numpy array
        query_vector = np.array(request.vector, dtype=np.float32)
        
        # Validate vector dimension
        if len(query_vector) != 1024:  # multilingual-e5-large dimension
            raise HTTPException(
                status_code=400,
                detail=f"Vector dimension phải là 1024, nhận được {len(query_vector)}"
            )
        
        # Search using FAISS store
        results = faiss_store.search_with_context(
            query_vector=query_vector,
            top_k=request.top_k,
            doc_id=request.doc_id
        )
        
        search_time = time.time() - start_time
        
        logger.info(f"✅ Vector search completed: {len(results)} results in {search_time:.3f}s")
        
        return SearchResponse(
            query="[Vector Search]",
            results=results,
            total_found=len(results),
            search_time=search_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in vector search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tìm kiếm vector: {str(e)}"
        )

@router.get("/search/document/{document_id}")
async def search_document_contexts(document_id: str) -> JSONResponse:
    """
    Lấy tất cả contexts của một document
    """
    try:
        contexts = faiss_store.get_contexts_by_document(document_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "document_id": document_id,
                "contexts": contexts,
                "total_contexts": len(contexts)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting document contexts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy contexts: {str(e)}"
        )

@router.post("/search/similar")
async def search_similar_contexts(request: SearchRequest) -> SearchResponse:
    """
    Tìm kiếm contexts tương tự với một đoạn text
    """
    try:
        import time
        start_time = time.time()
        
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query không được để trống"
            )
        
        # Search similar contexts
        results = faiss_store.search_similar_contexts(
            context_text=request.query.strip(),
            top_k=request.top_k,
            doc_id=request.doc_id,
            embedding_service=embedding_service
        )
        
        search_time = time.time() - start_time
        
        logger.info(f"✅ Similar contexts search completed: {len(results)} results in {search_time:.3f}s")
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_found=len(results),
            search_time=search_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in similar contexts search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tìm kiếm contexts tương tự: {str(e)}"
        )

@router.get("/search/stats")
async def get_search_stats() -> JSONResponse:
    """
    Lấy thống kê về search system
    """
    try:
        faiss_stats = faiss_store.get_stats()
        
        stats = {
            "faiss_store": faiss_stats,
            "search_capabilities": {
                "text_search": True,
                "vector_search": True,
                "document_filter": True,
                "similarity_search": True
            }
        }
        
        return JSONResponse(
            status_code=200,
            content=stats
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting search stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy thống kê: {str(e)}"
        )

@router.post("/search/embed")
async def embed_and_search(request: SearchRequest) -> SearchResponse:
    """
    Tạo embedding từ text và tìm kiếm (convenience endpoint)
    """
    try:
        import time
        start_time = time.time()
        
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query không được để trống"
            )
        
        # Generate embedding
        embedding = embedding_service.generate_embedding(request.query.strip())
        query_vector = np.array(embedding, dtype=np.float32)
        
        # Search with context
        results = faiss_store.search_with_context(
            query_vector=query_vector,
            top_k=request.top_k,
            doc_id=request.doc_id
        )
        
        search_time = time.time() - start_time
        
        logger.info(f"✅ Embed and search completed: {len(results)} results in {search_time:.3f}s")
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_found=len(results),
            search_time=search_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in embed and search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi embed và tìm kiếm: {str(e)}"
        )
