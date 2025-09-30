"""
Pydantic schemas
Định nghĩa các model và schema cho API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    """Trạng thái tài liệu"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"

class ChatRole(str, Enum):
    """Role trong chat"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# Document Schemas
class DocumentBase(BaseModel):
    """Base schema cho document"""
    filename: str = Field(..., description="Tên file")
    size: int = Field(..., description="Kích thước file (bytes)")

class DocumentCreate(DocumentBase):
    """Schema cho tạo document"""
    pass

class DocumentUpdate(BaseModel):
    """Schema cho cập nhật document"""
    status: Optional[DocumentStatus] = None
    chunks_count: Optional[int] = None

class DocumentResponse(DocumentBase):
    """Schema cho response document"""
    id: str = Field(..., description="ID của document")
    upload_time: datetime = Field(..., description="Thời gian upload")
    processed: bool = Field(..., description="Đã xử lý chưa")
    chunks_count: Optional[int] = Field(None, description="Số lượng chunks")
    status: DocumentStatus = Field(..., description="Trạng thái")
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    """Schema cho danh sách documents"""
    documents: List[DocumentResponse]
    total: int = Field(..., description="Tổng số documents")
    page: int = Field(..., description="Trang hiện tại")
    limit: int = Field(..., description="Số items per page")

# Chunk Schemas
class ChunkBase(BaseModel):
    """Base schema cho chunk"""
    content: str = Field(..., description="Nội dung chunk")
    page_number: Optional[int] = Field(None, description="Số trang")
    start_pos: Optional[int] = Field(None, description="Vị trí bắt đầu")
    end_pos: Optional[int] = Field(None, description="Vị trí kết thúc")

class ChunkResponse(ChunkBase):
    """Schema cho response chunk"""
    id: str = Field(..., description="ID của chunk")
    document_id: str = Field(..., description="ID của document")
    embedding_id: Optional[str] = Field(None, description="ID trong FAISS")
    
    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessage(BaseModel):
    """Schema cho chat message"""
    role: ChatRole = Field(..., description="Role của message")
    content: str = Field(..., description="Nội dung message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Thời gian")
    
    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

class ChatRequest(BaseModel):
    """Schema cho chat request"""
    message: str = Field(..., description="Tin nhắn của user", min_length=1, max_length=2000)
    document_id: Optional[str] = Field(None, description="ID document cụ thể (nếu None thì search toàn bộ)")
    max_tokens: int = Field(1000, description="Số tokens tối đa", ge=100, le=4000)
    temperature: float = Field(0.7, description="Temperature cho LLM", ge=0.0, le=2.0)
    top_k: int = Field(5, description="Số chunks liên quan nhất", ge=1, le=20)
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class ChatSource(BaseModel):
    """Schema cho source trong chat response"""
    chunk_id: str = Field(..., description="ID của chunk")
    content: str = Field(..., description="Nội dung chunk (preview)")
    document_id: str = Field(..., description="ID của document")
    similarity_score: float = Field(..., description="Điểm tương đồng", ge=0.0, le=1.0)
    page_number: Optional[int] = Field(None, description="Số trang")

class ChatResponse(BaseModel):
    """Schema cho chat response"""
    response: str = Field(..., description="Câu trả lời từ chatbot")
    sources: List[ChatSource] = Field(..., description="Các nguồn được sử dụng")
    processing_time: float = Field(..., description="Thời gian xử lý (seconds)")
    tokens_used: Optional[int] = Field(None, description="Số tokens đã sử dụng")
    model_used: str = Field(..., description="Model được sử dụng")

# Processing Schemas
class ProcessDocumentRequest(BaseModel):
    """Schema cho request xử lý document"""
    chunk_size: int = Field(500, description="Kích thước chunk", ge=100, le=2000)
    chunk_overlap: int = Field(50, description="Overlap giữa các chunks", ge=0, le=500)
    
    @validator('chunk_overlap')
    def chunk_overlap_valid(cls, v, values):
        if 'chunk_size' in values and v >= values['chunk_size']:
            raise ValueError('chunk_overlap must be less than chunk_size')
        return v

class ProcessDocumentResponse(BaseModel):
    """Schema cho response xử lý document"""
    document_id: str = Field(..., description="ID của document")
    chunks_created: int = Field(..., description="Số chunks đã tạo")
    processing_time: str = Field(..., description="Thời gian xử lý")
    status: str = Field(..., description="Trạng thái xử lý")

# Health Check Schemas
class HealthResponse(BaseModel):
    """Schema cho health check"""
    status: str = Field(..., description="Trạng thái hệ thống")
    message: str = Field(..., description="Thông báo")
    timestamp: datetime = Field(default_factory=datetime.now, description="Thời gian check")
    version: str = Field(..., description="Phiên bản API")

class DetailedHealthResponse(BaseModel):
    """Schema cho detailed health check"""
    status: str = Field(..., description="Trạng thái tổng thể")
    components: Dict[str, Any] = Field(..., description="Trạng thái các component")
    timestamp: datetime = Field(default_factory=datetime.now, description="Thời gian check")

# Error Schemas
class ErrorResponse(BaseModel):
    """Schema cho error response"""
    error: str = Field(..., description="Loại lỗi")
    detail: str = Field(..., description="Chi tiết lỗi")
    timestamp: datetime = Field(default_factory=datetime.now, description="Thời gian lỗi")

# Upload Schemas
class UploadResponse(BaseModel):
    """Schema cho upload response"""
    message: str = Field(..., description="Thông báo")
    document_id: str = Field(..., description="ID của document")
    filename: str = Field(..., description="Tên file")
    size: int = Field(..., description="Kích thước file")

# Session Schemas
class ChatSession(BaseModel):
    """Schema cho chat session"""
    session_id: str = Field(..., description="ID của session")
    created_at: datetime = Field(..., description="Thời gian tạo")
    last_activity: datetime = Field(..., description="Hoạt động cuối")
    message_count: int = Field(..., description="Số tin nhắn")

class ChatHistoryResponse(BaseModel):
    """Schema cho chat history response"""
    messages: List[ChatMessage] = Field(..., description="Danh sách tin nhắn")
    session_id: str = Field(..., description="ID của session")
    total: int = Field(..., description="Tổng số tin nhắn")
    page: int = Field(..., description="Trang hiện tại")
    limit: int = Field(..., description="Số items per page")
