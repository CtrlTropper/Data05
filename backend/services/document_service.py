"""
Document Service
Xử lý logic liên quan đến tài liệu với OCR support
"""

import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    """Service xử lý tài liệu với OCR support"""
    
    def __init__(self):
        self.upload_dir = "uploads"
        self.metadata_db = {}  # Placeholder for database
        self.pdf_processor = None  # Will be injected
    
    async def upload_document(self, file_content: bytes, filename: str, force_ocr: bool = False) -> Dict[str, Any]:
        """
        Upload và lưu tài liệu với OCR support
        
        Args:
            file_content: Nội dung file
            filename: Tên file
            force_ocr: Bắt buộc sử dụng OCR (default: False)
            
        Returns:
            Dict[str, Any]: Document info với processing details
        """
        try:
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Save file
            file_path = os.path.join(self.upload_dir, f"{document_id}_{filename}")
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Process document content
            processing_info = await self._process_document_content(file_path, filename, force_ocr)
            
            # Create document record
            document_info = {
                "id": document_id,
                "filename": filename,
                "file_path": file_path,
                "size": len(file_content),
                "upload_time": datetime.now().isoformat(),
                "processed": False,
                "chunks_count": 0,
                "processing_info": processing_info
            }
            
            # Save metadata
            self.metadata_db[document_id] = document_info
            
            logger.info(f"✅ Document uploaded: {document_id}")
            return document_info
            
        except Exception as e:
            logger.error(f"❌ Error uploading document: {e}")
            raise
    
    async def _process_document_content(self, file_path: str, filename: str, force_ocr: bool = False) -> Dict[str, Any]:
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
                return await self._process_pdf(file_path, force_ocr)
            elif file_ext in ['txt', 'md']:
                return await self._process_text_file(file_path)
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
    
    async def _process_pdf(self, file_path: str, force_ocr: bool = False) -> Dict[str, Any]:
        """
        Xử lý file PDF với OCR support
        
        Args:
            file_path: Đường dẫn file PDF
            force_ocr: Bắt buộc sử dụng OCR
            
        Returns:
            Dict[str, Any]: PDF processing information
        """
        try:
            if not self.pdf_processor:
                logger.warning("⚠️ PDF processor not available, skipping PDF processing")
                return {
                    'processing_type': 'skipped',
                    'message': 'PDF processor not available'
                }
            
            # Process PDF
            extracted_text, metadata = self.pdf_processor.process_pdf(file_path, force_ocr)
            
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
    
    async def _process_text_file(self, file_path: str) -> Dict[str, Any]:
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
    
    async def get_documents(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy danh sách tài liệu
        """
        try:
            # TODO: Implement database query
            documents = list(self.metadata_db.values())
            
            # Apply pagination
            return documents[skip:skip + limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting documents: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin một tài liệu
        """
        try:
            return self.metadata_db.get(document_id)
            
        except Exception as e:
            logger.error(f"❌ Error getting document: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Xóa tài liệu
        """
        try:
            if document_id not in self.metadata_db:
                return False
            
            document_info = self.metadata_db[document_id]
            
            # Delete file
            if os.path.exists(document_info["file_path"]):
                os.remove(document_info["file_path"])
            
            # Remove from metadata
            del self.metadata_db[document_id]
            
            # TODO: Remove from FAISS index
            
            logger.info(f"✅ Document deleted: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting document: {e}")
            raise
    
    async def process_document(self, document_id: str, chunk_size: int = 500, chunk_overlap: int = 50) -> Dict[str, Any]:
        """
        Xử lý tài liệu để tạo embeddings
        """
        try:
            if document_id not in self.metadata_db:
                raise ValueError("Document not found")
            
            document_info = self.metadata_db[document_id]
            
            # TODO: Implement document processing
            # 1. Parse document content (PDF, DOCX, TXT)
            # 2. Chunk text
            # 3. Generate embeddings
            # 4. Store in FAISS
            # 5. Update document status
            
            # Placeholder processing
            chunks_created = 10  # Placeholder
            
            # Update document status
            document_info["processed"] = True
            document_info["chunks_count"] = chunks_created
            document_info["processed_time"] = datetime.now().isoformat()
            
            logger.info(f"✅ Document processed: {document_id}")
            
            return {
                "document_id": document_id,
                "chunks_created": chunks_created,
                "processing_time": "5.2s",  # Placeholder
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing document: {e}")
            raise
    
    async def get_document_chunks(self, document_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lấy danh sách chunks của tài liệu
        """
        try:
            # TODO: Implement get chunks logic
            # Query chunks from database/FAISS
            
            return []  # Placeholder
            
        except Exception as e:
            logger.error(f"❌ Error getting document chunks: {e}")
            raise

# Global document service instance
document_service = DocumentService()
