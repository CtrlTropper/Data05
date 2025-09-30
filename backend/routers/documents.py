"""
Documents management router
Router quản lý tài liệu (upload, xóa, chọn tài liệu)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import uuid
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Global metadata storage
DOCUMENTS_METADATA = {}
METADATA_FILE = "data/documents_metadata.json"

# Ensure data directory exists
Path("data/docs").mkdir(parents=True, exist_ok=True)
Path("data").mkdir(parents=True, exist_ok=True)

def load_metadata():
    """Load metadata từ file JSON"""
    global DOCUMENTS_METADATA
    try:
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                DOCUMENTS_METADATA = json.load(f)
            logger.info(f"✅ Loaded {len(DOCUMENTS_METADATA)} documents metadata")
        else:
            DOCUMENTS_METADATA = {}
            logger.info("🆕 Created new metadata storage")
    except Exception as e:
        logger.error(f"❌ Error loading metadata: {e}")
        DOCUMENTS_METADATA = {}

def save_metadata():
    """Save metadata vào file JSON"""
    try:
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(DOCUMENTS_METADATA, f, ensure_ascii=False, indent=2)
        logger.info("💾 Metadata saved successfully")
    except Exception as e:
        logger.error(f"❌ Error saving metadata: {e}")

def validate_file_type(filename: str) -> bool:
    """Validate file type (chỉ cho phép PDF và TXT)"""
    allowed_extensions = ['.pdf', '.txt']
    file_ext = Path(filename).suffix.lower()
    return file_ext in allowed_extensions

def get_file_size(file_path: str) -> int:
    """Lấy kích thước file"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0

class DocumentResponse(BaseModel):
    """Response model cho document"""
    id: str
    filename: str
    size: int
    upload_time: str
    file_path: str
    file_type: str
    selected: bool = False

class DocumentListResponse(BaseModel):
    """Response model cho danh sách documents"""
    documents: List[DocumentResponse]
    total: int

class SelectDocumentRequest(BaseModel):
    """Request model cho chọn tài liệu"""
    selected: bool = True

# Import PDF processor
from services.pdf_processor import pdf_processor

# Load metadata khi khởi động
load_metadata()

async def process_document_content(file_path: str, filename: str, force_ocr: bool = False) -> Dict[str, Any]:
    """
    Xử lý nội dung tài liệu (PDF với OCR support)
    
    Args:
        file_path: Đường dẫn file
        filename: Tên file
        force_ocr: Bắt buộc sử dụng OCR
        
    Returns:
        Dict[str, Any]: Processing information
    """
    try:
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            return await process_pdf_with_ocr(file_path, force_ocr)
        elif file_ext in ['txt', 'md']:
            return await process_text_file(file_path)
        else:
            return {
                'processing_type': 'unsupported',
                'message': f'File type .{file_ext} is not supported yet'
            }
            
    except Exception as e:
        logger.error(f"❌ Error processing document content: {e}")
        return {
            'processing_type': 'error',
            'error': str(e)
        }

async def process_pdf_with_ocr(file_path: str, force_ocr: bool = False) -> Dict[str, Any]:
    """
    Xử lý file PDF với OCR support
    
    Args:
        file_path: Đường dẫn file PDF
        force_ocr: Bắt buộc sử dụng OCR
        
    Returns:
        Dict[str, Any]: PDF processing information
    """
    try:
        if not pdf_processor.is_initialized:
            logger.warning("⚠️ PDF processor not initialized, attempting to initialize...")
            await pdf_processor.initialize()
        
        # Process PDF
        extracted_text, metadata = pdf_processor.process_pdf(file_path, force_ocr)
        
        # Save extracted text to file
        text_file_path = file_path.replace('.pdf', '_extracted.txt')
        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        
        # Update metadata with text file path
        metadata['extracted_text_file'] = text_file_path
        metadata['text_length'] = len(extracted_text)
        
        logger.info(f"✅ PDF processed: {metadata['processing_type']}, {metadata['total_pages']} pages")
        return metadata
        
    except Exception as e:
        logger.error(f"❌ Error processing PDF: {e}")
        return {
            'processing_type': 'error',
            'error': str(e)
        }

async def process_text_file(file_path: str) -> Dict[str, Any]:
    """
    Xử lý file text
    
    Args:
        file_path: Đường dẫn file text
        
    Returns:
        Dict[str, Any]: Text processing information
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'processing_type': 'text-based',
            'text_length': len(content),
            'total_pages': 1,
            'ocr_language': None
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing text file: {e}")
        return {
            'processing_type': 'error',
            'error': str(e)
        }

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    force_ocr: bool = Form(False)
) -> JSONResponse:
    """
    Upload tài liệu mới (PDF/TXT)
    """
    try:
        # Validate file type
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Chỉ hỗ trợ file PDF và TXT"
            )
        
        # Validate file size (50MB max)
        max_size = 50 * 1024 * 1024  # 50MB
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=400,
                detail="File quá lớn. Kích thước tối đa là 50MB"
            )
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Create safe filename
        safe_filename = f"{document_id}_{file.filename}"
        file_path = os.path.join("data/docs", safe_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get actual file size
        actual_size = get_file_size(file_path)
        
        # Process document content (PDF with OCR support)
        processing_info = await process_document_content(file_path, file.filename, force_ocr)
        
        # Add to vector store with Uploads category
        from services.data_initialization import data_initialization_service
        vector_result = await data_initialization_service.add_uploaded_document(file_path, file.filename)
        if vector_result.get("success"):
            processing_info["vector_store"] = {
                "added": True,
                "chunks_created": vector_result.get("chunks_created", 0),
                "category": "Uploads"
            }
        else:
            processing_info["vector_store"] = {
                "added": False,
                "error": vector_result.get("error", "Unknown error")
            }
        
        # Create metadata
        document_metadata = {
            "id": document_id,
            "filename": file.filename,
            "file_path": file_path,
            "size": actual_size,
            "upload_time": datetime.now().isoformat(),
            "file_type": Path(file.filename).suffix.lower(),
            "selected": False,
            "processing_info": processing_info
        }
        
        # Save to metadata
        DOCUMENTS_METADATA[document_id] = document_metadata
        save_metadata()
        
        logger.info(f"✅ Document uploaded: {document_id} - {file.filename}")
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "Tài liệu đã được upload thành công",
                "document_id": document_id,
                "filename": file.filename,
                "size": actual_size,
                "file_type": document_metadata["file_type"],
                "processing_info": processing_info
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error uploading document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi upload tài liệu: {str(e)}"
        )

@router.get("/documents", response_model=DocumentListResponse)
async def get_documents(
    skip: int = 0,
    limit: int = 100
) -> DocumentListResponse:
    """
    Lấy danh sách tài liệu
    """
    try:
        # Load latest metadata
        load_metadata()
        
        # Convert to list and sort by upload time (newest first)
        documents_list = list(DOCUMENTS_METADATA.values())
        documents_list.sort(key=lambda x: x["upload_time"], reverse=True)
        
        # Apply pagination
        total = len(documents_list)
        paginated_docs = documents_list[skip:skip + limit]
        
        # Convert to response format
        response_docs = [
            DocumentResponse(
                id=doc["id"],
                filename=doc["filename"],
                size=doc["size"],
                upload_time=doc["upload_time"],
                file_path=doc["file_path"],
                file_type=doc["file_type"],
                selected=doc.get("selected", False)
            )
            for doc in paginated_docs
        ]
        
        return DocumentListResponse(
            documents=response_docs,
            total=total
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy danh sách tài liệu: {str(e)}"
        )

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str) -> DocumentResponse:
    """
    Lấy thông tin chi tiết một tài liệu
    """
    try:
        # Load latest metadata
        load_metadata()
        
        if document_id not in DOCUMENTS_METADATA:
            raise HTTPException(
                status_code=404, 
                detail="Không tìm thấy tài liệu"
            )
        
        doc = DOCUMENTS_METADATA[document_id]
        
        return DocumentResponse(
            id=doc["id"],
            filename=doc["filename"],
            size=doc["size"],
            upload_time=doc["upload_time"],
            file_path=doc["file_path"],
            file_type=doc["file_type"],
            selected=doc.get("selected", False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy thông tin tài liệu: {str(e)}"
        )

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str) -> JSONResponse:
    """
    Xóa tài liệu
    """
    try:
        # Load latest metadata
        load_metadata()
        
        if document_id not in DOCUMENTS_METADATA:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy tài liệu"
            )
        
        doc = DOCUMENTS_METADATA[document_id]
        file_path = doc["file_path"]
        
        # Delete file if exists
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"🗑️ Deleted file: {file_path}")
        
        # Remove from metadata
        del DOCUMENTS_METADATA[document_id]
        save_metadata()
        
        logger.info(f"✅ Document deleted: {document_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Tài liệu đã được xóa thành công",
                "document_id": document_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xóa tài liệu: {str(e)}"
        )

@router.post("/documents/{document_id}/select")
async def select_document(
    document_id: str,
    request: SelectDocumentRequest
) -> JSONResponse:
    """
    Chọn/bỏ chọn tài liệu để hỏi
    """
    try:
        # Load latest metadata
        load_metadata()
        
        if document_id not in DOCUMENTS_METADATA:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy tài liệu"
            )
        
        # Update selection status
        DOCUMENTS_METADATA[document_id]["selected"] = request.selected
        save_metadata()
        
        action = "chọn" if request.selected else "bỏ chọn"
        logger.info(f"✅ Document {action}: {document_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Tài liệu đã được {action} thành công",
                "document_id": document_id,
                "selected": request.selected
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error selecting document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi chọn tài liệu: {str(e)}"
        )

@router.get("/documents/selected")
async def get_selected_documents() -> JSONResponse:
    """
    Lấy danh sách tài liệu đã được chọn
    """
    try:
        # Load latest metadata
        load_metadata()
        
        selected_docs = [
            {
                "id": doc["id"],
                "filename": doc["filename"],
                "size": doc["size"],
                "upload_time": doc["upload_time"],
                "file_type": doc["file_type"]
            }
            for doc in DOCUMENTS_METADATA.values()
            if doc.get("selected", False)
        ]
        
        return JSONResponse(
            status_code=200,
            content={
                "selected_documents": selected_docs,
                "count": len(selected_docs)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting selected documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy tài liệu đã chọn: {str(e)}"
        )

@router.get("/documents/{document_id}/content")
async def get_document_content(document_id: str) -> JSONResponse:
    """
    Lấy nội dung tài liệu (chỉ cho file TXT)
    """
    try:
        # Load latest metadata
        load_metadata()
        
        if document_id not in DOCUMENTS_METADATA:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy tài liệu"
            )
        
        doc = DOCUMENTS_METADATA[document_id]
        
        # Chỉ hỗ trợ file TXT
        if doc["file_type"] != ".txt":
            raise HTTPException(
                status_code=400,
                detail="Chỉ hỗ trợ xem nội dung file TXT"
            )
        
        # Read file content
        file_path = doc["file_path"]
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="File không tồn tại"
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return JSONResponse(
            status_code=200,
            content={
                "document_id": document_id,
                "filename": doc["filename"],
                "content": content,
                "content_length": len(content)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting document content: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi đọc nội dung tài liệu: {str(e)}"
        )
