"""
Vector Service - Tích hợp Embedding và FAISS
Service chính để xử lý vector operations
"""

import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path

from .embedding_service import embedding_service
from ..db.faiss_store import faiss_store

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        """
        Khởi tạo Vector Service
        """
        self.embedding_service = embedding_service
        self.faiss_store = faiss_store
        self.is_initialized = False
        
        logger.info("Vector Service initialized")

    async def initialize(self):
        """
        Khởi tạo các services
        """
        try:
            logger.info("🚀 Initializing Vector Service...")
            
            # Load embedding model
            await self.embedding_service.load_model()
            
            # Load FAISS index
            self.faiss_store.load_index()
            
            self.is_initialized = True
            logger.info("✅ Vector Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing Vector Service: {e}")
            raise

    async def cleanup(self):
        """
        Cleanup resources
        """
        try:
            logger.info("🧹 Cleaning up Vector Service...")
            
            # Save FAISS index
            self.faiss_store.save_index()
            
            # Cleanup embedding service
            await self.embedding_service.cleanup()
            
            self.is_initialized = False
            logger.info("✅ Vector Service cleaned up")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up Vector Service: {e}")
            raise

    def add_document(self, 
                    text: str, 
                    doc_id: str, 
                    chunk_index: int = 0,
                    filename: str = "") -> str:
        """
        Thêm một document vào vector database
        
        Args:
            text: Nội dung text
            doc_id: ID của document
            chunk_index: Index của chunk
            filename: Tên file
            
        Returns:
            str: Chunk ID
        """
        if not self.is_initialized:
            raise RuntimeError("Vector Service not initialized. Call initialize() first.")
        
        try:
            chunk_id = self.faiss_store.add_document(
                text=text,
                doc_id=doc_id,
                chunk_index=chunk_index,
                filename=filename,
                embedding_service=self.embedding_service
            )
            
            logger.info(f"✅ Added document chunk: {chunk_id}")
            return chunk_id
            
        except Exception as e:
            logger.error(f"❌ Error adding document: {e}")
            raise

    def add_document_chunks(self, 
                           chunks: List[str], 
                           doc_id: str,
                           filename: str = "") -> List[str]:
        """
        Thêm nhiều chunks của document
        
        Args:
            chunks: Danh sách text chunks
            doc_id: ID của document
            filename: Tên file
            
        Returns:
            List[str]: Danh sách chunk IDs
        """
        if not self.is_initialized:
            raise RuntimeError("Vector Service not initialized. Call initialize() first.")
        
        try:
            chunk_ids = self.faiss_store.add_document_chunks(
                chunks=chunks,
                doc_id=doc_id,
                filename=filename,
                embedding_service=self.embedding_service
            )
            
            logger.info(f"✅ Added {len(chunks)} chunks for document {doc_id}")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"❌ Error adding document chunks: {e}")
            raise

    def search(self, 
               query: str, 
               top_k: int = 5, 
               doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Tìm kiếm vectors tương tự
        
        Args:
            query: Text query
            top_k: Số lượng kết quả
            doc_id: Nếu có, chỉ tìm trong document này
            
        Returns:
            List[Dict]: Kết quả tìm kiếm
        """
        if not self.is_initialized:
            raise RuntimeError("Vector Service not initialized. Call initialize() first.")
        
        try:
            results = self.faiss_store.search_text(
                query_text=query,
                top_k=top_k,
                doc_id=doc_id,
                embedding_service=self.embedding_service
            )
            
            logger.info(f"✅ Search completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching: {e}")
            raise

    def clear_doc(self, doc_id: str) -> bool:
        """
        Xóa document khỏi vector database
        
        Args:
            doc_id: ID của document
            
        Returns:
            bool: True nếu xóa thành công
        """
        if not self.is_initialized:
            raise RuntimeError("Vector Service not initialized. Call initialize() first.")
        
        try:
            success = self.faiss_store.clear_doc(doc_id)
            
            if success:
                logger.info(f"✅ Cleared document: {doc_id}")
            else:
                logger.warning(f"⚠️ Failed to clear document: {doc_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error clearing document: {e}")
            raise

    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Lấy tất cả chunks của document
        
        Args:
            doc_id: ID của document
            
        Returns:
            List[Dict]: Danh sách chunks
        """
        if not self.is_initialized:
            raise RuntimeError("Vector Service not initialized. Call initialize() first.")
        
        try:
            chunks = self.faiss_store.get_document_chunks(doc_id)
            logger.info(f"✅ Retrieved {len(chunks)} chunks for document {doc_id}")
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Error getting document chunks: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê về vector database
        """
        try:
            embedding_stats = self.embedding_service.get_model_info()
            faiss_stats = self.faiss_store.get_stats()
            
            stats = {
                "embedding_service": embedding_stats,
                "faiss_store": faiss_stats,
                "vector_service": {
                    "initialized": self.is_initialized,
                    "total_vectors": faiss_stats.get("total_vectors", 0),
                    "total_documents": faiss_stats.get("total_documents", 0)
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {"error": str(e)}

    def backup(self, backup_path: str):
        """
        Backup vector database
        """
        if not self.is_initialized:
            raise RuntimeError("Vector Service not initialized. Call initialize() first.")
        
        try:
            self.faiss_store.backup(backup_path)
            logger.info(f"✅ Backed up vector database to {backup_path}")
            
        except Exception as e:
            logger.error(f"❌ Error backing up: {e}")
            raise

    def clear_all(self):
        """
        Xóa tất cả dữ liệu
        """
        if not self.is_initialized:
            raise RuntimeError("Vector Service not initialized. Call initialize() first.")
        
        try:
            self.faiss_store.clear_all()
            logger.info("✅ Cleared all vector data")
            
        except Exception as e:
            logger.error(f"❌ Error clearing all data: {e}")
            raise

    def validate_query(self, query: str) -> bool:
        """
        Validate query text
        """
        if not query or not query.strip():
            return False
        
        if len(query.strip()) < 2:
            return False
        
        return True

    def chunk_text(self, 
                   text: str, 
                   chunk_size: int = 500, 
                   chunk_overlap: int = 50) -> List[str]:
        """
        Chia text thành chunks
        
        Args:
            text: Text cần chia
            chunk_size: Kích thước chunk
            chunk_overlap: Độ chồng lấp giữa các chunks
            
        Returns:
            List[str]: Danh sách chunks
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
                # Tìm dấu câu gần nhất
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Tính start cho chunk tiếp theo
            start = end - chunk_overlap
            if start >= len(text):
                break
        
        logger.info(f"✅ Chunked text into {len(chunks)} chunks")
        return chunks

# Global instance
vector_service = VectorService()
