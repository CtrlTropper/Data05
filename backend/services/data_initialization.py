"""
Data Initialization Service
Tự động load và embedding dữ liệu ban đầu khi khởi động hệ thống
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class DataInitializationService:
    """Service khởi tạo dữ liệu ban đầu"""
    
    def __init__(self):
        self.data_dir = "data"
        self.categories = {
            "Luat": "Luat",
            "TaiLieuTiengViet": "TaiLieuTiengViet", 
            "TaiLieuTiengAnh": "TaiLieuTiengAnh",
            "Uploads": "uploads"
        }
        self.supported_extensions = ['.pdf', '.txt', '.md', '.docx']
        self.is_initialized = False
        self.embedding_service = None
        self.vector_service = None
        self.pdf_processor = None
        
    async def initialize(self, embedding_service, vector_service, pdf_processor):
        """Khởi tạo service với dependencies"""
        try:
            self.embedding_service = embedding_service
            self.vector_service = vector_service
            self.pdf_processor = pdf_processor
            
            # Tạo các thư mục cần thiết
            await self._create_directories()
            
            # Load dữ liệu ban đầu
            await self._load_initial_data()
            
            self.is_initialized = True
            logger.info("✅ Data Initialization Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing Data Initialization Service: {e}")
            raise
    
    async def _create_directories(self):
        """Tạo các thư mục cần thiết"""
        try:
            # Tạo thư mục data nếu chưa có
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Tạo các thư mục category
            for category in self.categories.values():
                category_path = os.path.join(self.data_dir, category)
                os.makedirs(category_path, exist_ok=True)
                logger.info(f"📁 Created directory: {category_path}")
            
            # Tạo thư mục uploads
            uploads_path = os.path.join(self.data_dir, "uploads")
            os.makedirs(uploads_path, exist_ok=True)
            logger.info(f"📁 Created directory: {uploads_path}")
            
        except Exception as e:
            logger.error(f"❌ Error creating directories: {e}")
            raise
    
    async def _load_initial_data(self):
        """Load và embedding dữ liệu ban đầu"""
        try:
            logger.info("🔄 Starting initial data loading...")
            
            total_documents = 0
            total_chunks = 0
            
            # Load từng category
            for category_name, category_path in self.categories.items():
                if category_name == "Uploads":
                    continue  # Skip uploads folder
                
                category_full_path = os.path.join(self.data_dir, category_path)
                
                if os.path.exists(category_full_path):
                    logger.info(f"📚 Loading documents from category: {category_name}")
                    
                    documents_processed, chunks_created = await self._process_category(
                        category_full_path, 
                        category_name
                    )
                    
                    total_documents += documents_processed
                    total_chunks += chunks_created
                    
                    logger.info(f"✅ Category {category_name}: {documents_processed} documents, {chunks_created} chunks")
                else:
                    logger.warning(f"⚠️ Category directory not found: {category_full_path}")
            
            logger.info(f"🎉 Initial data loading completed: {total_documents} documents, {total_chunks} chunks")
            
        except Exception as e:
            logger.error(f"❌ Error loading initial data: {e}")
            raise
    
    async def _process_category(self, category_path: str, category_name: str) -> tuple[int, int]:
        """
        Xử lý tất cả tài liệu trong một category
        
        Args:
            category_path: Đường dẫn thư mục category
            category_name: Tên category
            
        Returns:
            tuple[int, int]: (số documents, số chunks)
        """
        try:
            documents_processed = 0
            chunks_created = 0
            
            # Tìm tất cả files trong category
            files = self._find_documents(category_path)
            
            if not files:
                logger.info(f"📂 No documents found in category: {category_name}")
                return 0, 0
            
            logger.info(f"📄 Found {len(files)} documents in category: {category_name}")
            
            # Xử lý từng file
            for file_path in files:
                try:
                    logger.info(f"🔄 Processing document: {os.path.basename(file_path)}")
                    
                    # Extract text from document
                    text_content = await self._extract_text_from_file(file_path)
                    
                    if text_content and text_content.strip():
                        # Create document ID
                        doc_id = self._generate_document_id(file_path, category_name)
                        
                        # Add to vector store with category metadata
                        chunks = await self.vector_service.add_document(
                            text=text_content,
                            doc_id=doc_id,
                            metadata={
                                "category": category_name,
                                "filename": os.path.basename(file_path),
                                "file_path": file_path,
                                "source": "initial_data",
                                "processed_at": datetime.now().isoformat()
                            }
                        )
                        
                        documents_processed += 1
                        chunks_created += len(chunks)
                        
                        logger.info(f"✅ Processed: {os.path.basename(file_path)} -> {len(chunks)} chunks")
                    else:
                        logger.warning(f"⚠️ No text extracted from: {os.path.basename(file_path)}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing document {file_path}: {e}")
                    continue
            
            return documents_processed, chunks_created
            
        except Exception as e:
            logger.error(f"❌ Error processing category {category_name}: {e}")
            return 0, 0
    
    def _find_documents(self, directory_path: str) -> List[str]:
        """
        Tìm tất cả documents trong thư mục
        
        Args:
            directory_path: Đường dẫn thư mục
            
        Returns:
            List[str]: Danh sách đường dẫn files
        """
        try:
            files = []
            directory = Path(directory_path)
            
            for ext in self.supported_extensions:
                pattern = f"**/*{ext}"
                found_files = list(directory.glob(pattern))
                files.extend([str(f) for f in found_files])
            
            return files
            
        except Exception as e:
            logger.error(f"❌ Error finding documents in {directory_path}: {e}")
            return []
    
    async def _extract_text_from_file(self, file_path: str) -> str:
        """
        Trích xuất text từ file
        
        Args:
            file_path: Đường dẫn file
            
        Returns:
            str: Text content
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                return await self._extract_text_from_pdf(file_path)
            elif file_ext in ['.txt', '.md']:
                return await self._extract_text_from_text_file(file_path)
            elif file_ext == '.docx':
                return await self._extract_text_from_docx(file_path)
            else:
                logger.warning(f"⚠️ Unsupported file type: {file_ext}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error extracting text from {file_path}: {e}")
            return ""
    
    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Trích xuất text từ PDF"""
        try:
            if not self.pdf_processor:
                logger.warning("⚠️ PDF processor not available")
                return ""
            
            # Process PDF (auto-detect type)
            extracted_text, metadata = self.pdf_processor.process_pdf(file_path, force_ocr=False)
            return extracted_text
            
        except Exception as e:
            logger.error(f"❌ Error extracting text from PDF {file_path}: {e}")
            return ""
    
    async def _extract_text_from_text_file(self, file_path: str) -> str:
        """Trích xuất text từ text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"❌ Error reading text file {file_path}: {e}")
            return ""
    
    async def _extract_text_from_docx(self, file_path: str) -> str:
        """Trích xuất text từ DOCX file"""
        try:
            # TODO: Implement DOCX text extraction
            # For now, return empty string
            logger.warning(f"⚠️ DOCX extraction not implemented yet: {file_path}")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error extracting text from DOCX {file_path}: {e}")
            return ""
    
    def _generate_document_id(self, file_path: str, category: str) -> str:
        """
        Tạo document ID từ file path và category
        
        Args:
            file_path: Đường dẫn file
            category: Category name
            
        Returns:
            str: Document ID
        """
        try:
            filename = os.path.basename(file_path)
            # Tạo ID từ category và filename
            doc_id = f"{category}_{filename}_{hash(file_path) % 10000}"
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Error generating document ID: {e}")
            return f"{category}_{os.path.basename(file_path)}"
    
    async def add_uploaded_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Thêm document được upload vào vector store
        
        Args:
            file_path: Đường dẫn file
            filename: Tên file
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            logger.info(f"🔄 Adding uploaded document: {filename}")
            
            # Extract text
            text_content = await self._extract_text_from_file(file_path)
            
            if not text_content or not text_content.strip():
                return {
                    "success": False,
                    "error": "No text extracted from document"
                }
            
            # Create document ID
            doc_id = self._generate_document_id(file_path, "Uploads")
            
            # Add to vector store
            chunks = await self.vector_service.add_document(
                text=text_content,
                doc_id=doc_id,
                metadata={
                    "category": "Uploads",
                    "filename": filename,
                    "file_path": file_path,
                    "source": "user_upload",
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            logger.info(f"✅ Added uploaded document: {filename} -> {len(chunks)} chunks")
            
            return {
                "success": True,
                "doc_id": doc_id,
                "chunks_created": len(chunks),
                "text_length": len(text_content)
            }
            
        except Exception as e:
            logger.error(f"❌ Error adding uploaded document: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_category_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê về các category
        
        Returns:
            Dict[str, Any]: Category statistics
        """
        try:
            stats = {}
            
            for category_name, category_path in self.categories.items():
                category_full_path = os.path.join(self.data_dir, category_path)
                
                if os.path.exists(category_full_path):
                    files = self._find_documents(category_full_path)
                    stats[category_name] = {
                        "path": category_full_path,
                        "document_count": len(files),
                        "exists": True
                    }
                else:
                    stats[category_name] = {
                        "path": category_full_path,
                        "document_count": 0,
                        "exists": False
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting category stats: {e}")
            return {}
    
    async def reload_category(self, category_name: str) -> Dict[str, Any]:
        """
        Reload một category cụ thể
        
        Args:
            category_name: Tên category
            
        Returns:
            Dict[str, Any]: Reload result
        """
        try:
            if category_name not in self.categories:
                return {
                    "success": False,
                    "error": f"Unknown category: {category_name}"
                }
            
            category_path = os.path.join(self.data_dir, self.categories[category_name])
            
            if not os.path.exists(category_path):
                return {
                    "success": False,
                    "error": f"Category directory not found: {category_path}"
                }
            
            logger.info(f"🔄 Reloading category: {category_name}")
            
            # Clear existing documents from this category
            # TODO: Implement clear by category in vector service
            
            # Process category
            documents_processed, chunks_created = await self._process_category(
                category_path, 
                category_name
            )
            
            logger.info(f"✅ Reloaded category {category_name}: {documents_processed} documents, {chunks_created} chunks")
            
            return {
                "success": True,
                "category": category_name,
                "documents_processed": documents_processed,
                "chunks_created": chunks_created
            }
            
        except Exception as e:
            logger.error(f"❌ Error reloading category {category_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global data initialization service instance
data_initialization_service = DataInitializationService()
