"""
FAISS Vector Store - Quản lý vector database với FAISS
Tích hợp với Embedding Service để lưu trữ và tìm kiếm vectors
"""

import os
import logging
import numpy as np
import faiss
import pickle
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class FAISSStore:
    def __init__(self, 
                 index_path: str = "data/faiss_index",
                 metadata_path: str = "data/metadata",
                 dimension: int = 1024):
        """
        Khởi tạo FAISS Store
        
        Args:
            index_path: Đường dẫn lưu FAISS index
            metadata_path: Đường dẫn lưu metadata
            dimension: Dimension của vector (multilingual-e5-large = 1024)
        """
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.dimension = dimension
        self.index = None
        self.metadata = []
        self.doc_metadata = {}  # {doc_id: {chunks: [], total_chunks: int}}
        
        # Tạo thư mục nếu chưa có
        os.makedirs(index_path, exist_ok=True)
        os.makedirs(metadata_path, exist_ok=True)
        
        logger.info(f"FAISS Store initialized. Dimension: {dimension}")
        logger.info(f"Index path: {index_path}")
        logger.info(f"Metadata path: {metadata_path}")

    def initialize_index(self):
        """
        Khởi tạo FAISS index
        """
        try:
            # Tạo IndexFlatIP (Inner Product) cho cosine similarity
            self.index = faiss.IndexFlatIP(self.dimension)
            logger.info("✅ FAISS index initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing FAISS index: {e}")
            raise

    def load_index(self):
        """
        Load FAISS index từ file
        """
        try:
            index_file = os.path.join(self.index_path, "faiss_index.bin")
            metadata_file = os.path.join(self.metadata_path, "metadata.json")
            doc_metadata_file = os.path.join(self.metadata_path, "doc_metadata.json")
            
            if os.path.exists(index_file):
                self.index = faiss.read_index(index_file)
                logger.info(f"✅ Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                self.initialize_index()
                logger.info("✅ Created new FAISS index")
            
            # Load metadata
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                logger.info(f"✅ Loaded {len(self.metadata)} metadata entries")
            
            # Load document metadata
            if os.path.exists(doc_metadata_file):
                with open(doc_metadata_file, 'r', encoding='utf-8') as f:
                    self.doc_metadata = json.load(f)
                logger.info(f"✅ Loaded metadata for {len(self.doc_metadata)} documents")
                
        except Exception as e:
            logger.error(f"❌ Error loading FAISS index: {e}")
            raise

    def save_index(self):
        """
        Lưu FAISS index và metadata
        """
        try:
            if self.index is None:
                logger.warning("No index to save")
                return
            
            # Save FAISS index
            index_file = os.path.join(self.index_path, "faiss_index.bin")
            faiss.write_index(self.index, index_file)
            
            # Save metadata
            metadata_file = os.path.join(self.metadata_path, "metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
            # Save document metadata
            doc_metadata_file = os.path.join(self.metadata_path, "doc_metadata.json")
            with open(doc_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.doc_metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Saved FAISS index with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"❌ Error saving FAISS index: {e}")
            raise

    def add_document(self, 
                    text: str, 
                    doc_id: str, 
                    chunk_index: int = 0,
                    filename: str = "",
                    embedding_service=None) -> str:
        """
        Thêm một document vào FAISS store
        
        Args:
            text: Nội dung text của document
            doc_id: ID của document
            chunk_index: Index của chunk trong document
            filename: Tên file
            embedding_service: Embedding service instance
            
        Returns:
            str: Chunk ID được tạo
        """
        if self.index is None:
            self.initialize_index()
        
        if embedding_service is None:
            raise ValueError("Embedding service is required")
        
        try:
            # Tạo embedding
            embedding = embedding_service.generate_embedding(text)
            
            # Normalize embedding cho cosine similarity
            embedding = embedding_service.normalize_embedding(embedding)
            
            # Validate embedding
            if not embedding_service.validate_embedding(embedding):
                raise ValueError("Invalid embedding generated")
            
            # Tạo chunk ID
            chunk_id = f"{doc_id}_{chunk_index}"
            
            # Thêm vào FAISS index
            self.index.add(embedding.reshape(1, -1))
            
            # Tạo metadata
            chunk_metadata = {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "chunk_index": chunk_index,
                "content": text,
                "filename": filename,
                "vector_index": self.index.ntotal - 1,  # Index trong FAISS
                "created_at": datetime.now().isoformat(),
                "embedding_dimension": self.dimension
            }
            
            self.metadata.append(chunk_metadata)
            
            # Update document metadata
            if doc_id not in self.doc_metadata:
                self.doc_metadata[doc_id] = {
                    "filename": filename,
                    "chunks": [],
                    "total_chunks": 0,
                    "created_at": datetime.now().isoformat()
                }
            
            self.doc_metadata[doc_id]["chunks"].append(chunk_id)
            self.doc_metadata[doc_id]["total_chunks"] += 1
            
            logger.info(f"✅ Added chunk {chunk_id} to FAISS store")
            return chunk_id
            
        except Exception as e:
            logger.error(f"❌ Error adding document to FAISS store: {e}")
            raise

    def add_document_chunks(self, 
                           chunks: List[str], 
                           doc_id: str,
                           filename: str = "",
                           embedding_service=None) -> List[str]:
        """
        Thêm nhiều chunks của một document
        
        Args:
            chunks: Danh sách các text chunks
            doc_id: ID của document
            filename: Tên file
            embedding_service: Embedding service instance
            
        Returns:
            List[str]: Danh sách chunk IDs được tạo
        """
        chunk_ids = []
        
        try:
            for i, chunk in enumerate(chunks):
                chunk_id = self.add_document(
                    text=chunk,
                    doc_id=doc_id,
                    chunk_index=i,
                    filename=filename,
                    embedding_service=embedding_service
                )
                chunk_ids.append(chunk_id)
            
            logger.info(f"✅ Added {len(chunks)} chunks for document {doc_id}")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"❌ Error adding document chunks: {e}")
            raise

    def search(self, 
               query_vector: np.ndarray, 
               top_k: int = 5, 
               doc_id: Optional[str] = None,
               category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Tìm kiếm vectors tương tự
        
        Args:
            query_vector: Vector query đã được normalize
            top_k: Số lượng kết quả trả về
            doc_id: Nếu có, chỉ tìm trong document này
            category: Nếu có, chỉ tìm trong category này
            
        Returns:
            List[Dict]: Danh sách kết quả với metadata
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("No vectors in index")
            return []
        
        try:
            # Tìm kiếm
            scores, indices = self.index.search(query_vector.reshape(1, -1), top_k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # FAISS trả về -1 nếu không đủ kết quả
                    continue
                
                # Lấy metadata
                if idx < len(self.metadata):
                    chunk_metadata = self.metadata[idx].copy()
                    chunk_metadata["similarity_score"] = float(score)
                    
                    # Filter theo doc_id và category nếu có
                    if doc_id is not None and chunk_metadata["doc_id"] != doc_id:
                        continue
                    
                    if category is not None and chunk_metadata.get("category") != category:
                        continue
                    
                    results.append(chunk_metadata)
            
            logger.info(f"✅ Found {len(results)} results for search")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching FAISS index: {e}")
            raise

    def search_text(self, 
                   query_text: str, 
                   top_k: int = 5, 
                   doc_id: Optional[str] = None,
                   category: Optional[str] = None,
                   embedding_service=None) -> List[Dict[str, Any]]:
        """
        Tìm kiếm bằng text query
        
        Args:
            query_text: Text query
            top_k: Số lượng kết quả
            doc_id: Nếu có, chỉ tìm trong document này
            category: Nếu có, chỉ tìm trong category này
            embedding_service: Embedding service instance
            
        Returns:
            List[Dict]: Danh sách kết quả
        """
        if embedding_service is None:
            raise ValueError("Embedding service is required")
        
        try:
            # Tạo embedding cho query
            query_embedding = embedding_service.generate_embedding(query_text)
            query_embedding = embedding_service.normalize_embedding(query_embedding)
            
            # Tìm kiếm
            return self.search(query_embedding, top_k, doc_id, category)
            
        except Exception as e:
            logger.error(f"❌ Error in text search: {e}")
            raise

    def clear_doc(self, doc_id: str) -> bool:
        """
        Xóa tất cả chunks của một document khỏi FAISS store
        
        Args:
            doc_id: ID của document cần xóa
            
        Returns:
            bool: True nếu xóa thành công
        """
        try:
            if doc_id not in self.doc_metadata:
                logger.warning(f"Document {doc_id} not found")
                return False
            
            # Lấy danh sách chunks cần xóa
            chunks_to_remove = self.doc_metadata[doc_id]["chunks"]
            
            if not chunks_to_remove:
                logger.warning(f"No chunks found for document {doc_id}")
                return False
            
            # Tạo index mới (FAISS không hỗ trợ xóa trực tiếp)
            new_index = faiss.IndexFlatIP(self.dimension)
            new_metadata = []
            
            # Copy các vectors không thuộc document này
            for i, chunk_metadata in enumerate(self.metadata):
                if chunk_metadata["doc_id"] != doc_id:
                    # Lấy vector từ index cũ
                    vector = self.index.reconstruct(i)
                    new_index.add(vector.reshape(1, -1))
                    
                    # Update vector index trong metadata
                    chunk_metadata["vector_index"] = new_index.ntotal - 1
                    new_metadata.append(chunk_metadata)
            
            # Thay thế index và metadata
            self.index = new_index
            self.metadata = new_metadata
            
            # Xóa document metadata
            del self.doc_metadata[doc_id]
            
            logger.info(f"✅ Removed document {doc_id} with {len(chunks_to_remove)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error clearing document {doc_id}: {e}")
            return False

    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Lấy tất cả chunks của một document
        
        Args:
            doc_id: ID của document
            
        Returns:
            List[Dict]: Danh sách chunks
        """
        try:
            chunks = []
            for chunk_metadata in self.metadata:
                if chunk_metadata["doc_id"] == doc_id:
                    chunks.append(chunk_metadata)
            
            # Sắp xếp theo chunk_index
            chunks.sort(key=lambda x: x["chunk_index"])
            
            logger.info(f"✅ Retrieved {len(chunks)} chunks for document {doc_id}")
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Error getting document chunks: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê về FAISS store
        """
        try:
            stats = {
                "total_vectors": self.index.ntotal if self.index else 0,
                "total_documents": len(self.doc_metadata),
                "total_chunks": len(self.metadata),
                "dimension": self.dimension,
                "index_type": "IndexFlatIP",
                "documents": {}
            }
            
            # Thống kê theo document
            for doc_id, doc_info in self.doc_metadata.items():
                stats["documents"][doc_id] = {
                    "filename": doc_info["filename"],
                    "chunks": doc_info["total_chunks"],
                    "created_at": doc_info["created_at"]
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {"error": str(e)}

    def clear_all(self):
        """
        Xóa tất cả dữ liệu trong FAISS store
        """
        try:
            self.initialize_index()
            self.metadata = []
            self.doc_metadata = {}
            
            logger.info("✅ Cleared all data from FAISS store")
            
        except Exception as e:
            logger.error(f"❌ Error clearing FAISS store: {e}")
            raise

    def backup(self, backup_path: str):
        """
        Backup FAISS store
        """
        try:
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup index
            if self.index:
                backup_index = os.path.join(backup_path, "faiss_index.bin")
                faiss.write_index(self.index, backup_index)
            
            # Backup metadata
            backup_metadata = os.path.join(backup_path, "metadata.json")
            with open(backup_metadata, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
            # Backup document metadata
            backup_doc_metadata = os.path.join(backup_path, "doc_metadata.json")
            with open(backup_doc_metadata, 'w', encoding='utf-8') as f:
                json.dump(self.doc_metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Backed up FAISS store to {backup_path}")
            
        except Exception as e:
            logger.error(f"❌ Error backing up FAISS store: {e}")
            raise

# Global instance
faiss_store = FAISSStore()