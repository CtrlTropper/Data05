"""
Embedding Router
API xử lý embedding cho documents
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Import services
from services.embedding_service import embedding_service
from db.faiss_store import faiss_store

logger = logging.getLogger(__name__)

router = APIRouter()

# Load documents metadata
METADATA_FILE = "data/documents_metadata.json"

def load_documents_metadata() -> Dict[str, Any]:
    """Load documents metadata"""
    try:
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"❌ Error loading documents metadata: {e}")
        return {}

class EmbedRequest(BaseModel):
    """Request model cho embed document"""
    chunk_size: int = 500
    chunk_overlap: int = 50

class EmbedResponse(BaseModel):
    """Response model cho embed document"""
    document_id: str
    chunks_created: int
    vectors_stored: int
    processing_time: float
    status: str

class TextEmbedRequest(BaseModel):
    """Request model cho embed text"""
    text: str

class TextEmbedResponse(BaseModel):
    """Response model cho embed text"""
    embedding: List[float]
    dimension: int
    text_length: int

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Chia text thành các chunks
    
    Args:
        text: Văn bản cần chia
        chunk_size: Kích thước mỗi chunk
        chunk_overlap: Overlap giữa các chunks
        
    Returns:
        List[str]: Danh sách các chunks
    """
    if not text or not text.strip():
        return []
    
    text = text.strip()
    
    # Nếu text ngắn hơn chunk_size, trả về toàn bộ
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Nếu không phải chunk cuối, tìm vị trí cắt phù hợp
        if end < len(text):
            # Tìm dấu câu hoặc khoảng trắng gần nhất
            for i in range(end, max(start + chunk_size // 2, end - 50), -1):
                if text[i] in '.!?。！？\n':
                    end = i + 1
                    break
                elif text[i] == ' ':
                    end = i
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Di chuyển start với overlap
        start = end - chunk_overlap
        if start >= len(text):
            break
    
    return chunks

def read_text_file(file_path: str) -> str:
    """
    Đọc nội dung file text
    
    Args:
        file_path: Đường dẫn file
        
    Returns:
        str: Nội dung file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Thử với encoding khác
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            raise ValueError("Không thể đọc file với encoding hiện tại")

@router.post("/embed/document/{document_id}", response_model=EmbedResponse)
async def embed_document(
    document_id: str,
    request: EmbedRequest
) -> EmbedResponse:
    """
    Tạo embedding cho document và lưu vào FAISS
    """
    try:
        start_time = datetime.now()
        
        # Load documents metadata
        documents_metadata = load_documents_metadata()
        
        if document_id not in documents_metadata:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy tài liệu"
            )
        
        doc_metadata = documents_metadata[document_id]
        file_path = doc_metadata["file_path"]
        file_type = doc_metadata["file_type"]
        
        # Kiểm tra file tồn tại
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="File không tồn tại"
            )
        
        # Đọc nội dung file
        if file_type == ".txt":
            text_content = read_text_file(file_path)
        elif file_type == ".pdf":
            # TODO: Implement PDF reading
            raise HTTPException(
                status_code=400,
                detail="PDF processing chưa được implement"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Không hỗ trợ file type: {file_type}"
            )
        
        if not text_content or not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail="File trống hoặc không có nội dung"
            )
        
        # Chia text thành chunks
        chunks = chunk_text(
            text_content, 
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Không thể chia file thành chunks"
            )
        
        # Tạo embeddings cho các chunks
        logger.info(f"📝 Creating embeddings for {len(chunks)} chunks...")
        
        embeddings = embedding_service.generate_embeddings_batch(chunks)
        
        if len(embeddings) != len(chunks):
            raise HTTPException(
                status_code=500,
                detail="Số lượng embeddings không khớp với số chunks"
            )
        
        # Chuẩn bị metadata cho FAISS
        vectors_metadata = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            metadata = {
                "document_id": document_id,
                "chunk_id": f"{document_id}_chunk_{i}",
                "chunk_index": i,
                "content": chunk,
                "content_length": len(chunk),
                "created_at": datetime.now().isoformat(),
                "filename": doc_metadata["filename"]
            }
            vectors_metadata.append(metadata)
        
        # Lưu vào FAISS
        import numpy as np
        vectors_array = np.array(embeddings, dtype=np.float32)
        vector_ids = faiss_store.add_vectors(vectors_array, vectors_metadata)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Document {document_id} embedded successfully")
        logger.info(f"📊 Chunks: {len(chunks)}, Vectors: {len(vector_ids)}")
        
        return EmbedResponse(
            document_id=document_id,
            chunks_created=len(chunks),
            vectors_stored=len(vector_ids),
            processing_time=processing_time,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error embedding document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tạo embedding: {str(e)}"
        )

@router.post("/embed/text", response_model=TextEmbedResponse)
async def embed_text(request: TextEmbedRequest) -> TextEmbedResponse:
    """
    Tạo embedding cho một đoạn text
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text không được để trống"
            )
        
        # Tạo embedding
        embedding = embedding_service.generate_embedding(request.text.strip())
        
        return TextEmbedResponse(
            embedding=embedding,
            dimension=len(embedding),
            text_length=len(request.text.strip())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error embedding text: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tạo embedding: {str(e)}"
        )

@router.get("/embed/stats")
async def get_embedding_stats() -> JSONResponse:
    """
    Lấy thống kê về embedding system
    """
    try:
        # Get FAISS stats
        faiss_stats = faiss_store.get_stats()
        
        # Get embedding service info
        embedding_info = embedding_service.get_model_info()
        
        # Get documents metadata
        documents_metadata = load_documents_metadata()
        
        stats = {
            "faiss_store": faiss_stats,
            "embedding_service": embedding_info,
            "documents": {
                "total_documents": len(documents_metadata),
                "processed_documents": len([
                    doc for doc in documents_metadata.values() 
                    if doc.get("processed", False)
                ])
            }
        }
        
        return JSONResponse(
            status_code=200,
            content=stats
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting embedding stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy thống kê: {str(e)}"
        )

@router.delete("/embed/document/{document_id}")
async def delete_document_embeddings(document_id: str) -> JSONResponse:
    """
    Xóa tất cả embeddings của một document
    """
    try:
        # Load documents metadata
        documents_metadata = load_documents_metadata()
        
        if document_id not in documents_metadata:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy tài liệu"
            )
        
        # Xóa vectors từ FAISS
        deleted_count = faiss_store.delete_document_vectors(document_id)
        
        logger.info(f"✅ Deleted {deleted_count} vectors for document {document_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Embeddings đã được xóa thành công",
                "document_id": document_id,
                "vectors_deleted": deleted_count
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting document embeddings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xóa embeddings: {str(e)}"
        )

@router.get("/embed/document/{document_id}/vectors")
async def get_document_vectors(document_id: str) -> JSONResponse:
    """
    Lấy thông tin về vectors của một document
    """
    try:
        # Load documents metadata
        documents_metadata = load_documents_metadata()
        
        if document_id not in documents_metadata:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy tài liệu"
            )
        
        # Lấy vectors từ FAISS
        vectors = faiss_store.get_document_vectors(document_id)
        
        # Chỉ trả về metadata, không trả về vector data
        vectors_info = []
        for vector in vectors:
            vector_info = {
                "vector_id": vector.get("vector_id"),
                "chunk_id": vector.get("chunk_id"),
                "chunk_index": vector.get("chunk_index"),
                "content_preview": vector.get("content", "")[:200] + "...",
                "content_length": vector.get("content_length"),
                "created_at": vector.get("created_at")
            }
            vectors_info.append(vector_info)
        
        return JSONResponse(
            status_code=200,
            content={
                "document_id": document_id,
                "vectors_count": len(vectors_info),
                "vectors": vectors_info
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting document vectors: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy thông tin vectors: {str(e)}"
        )
