"""
Vector Database với FAISS
Xử lý lưu trữ và tìm kiếm vector embeddings
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorDB:
    """Vector Database sử dụng FAISS"""
    
    def __init__(self, dimension: int = 768, index_path: str = "data/faiss_index"):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.metadata_path = self.index_path / "metadata.pkl"
        
        # FAISS index
        self.index: Optional[faiss.IndexFlatIP] = None  # Inner Product for cosine similarity
        self.metadata: List[Dict[str, Any]] = []
        
        # Create directory if not exists
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index từ disk"""
        try:
            index_file = self.index_path / "faiss_index.bin"
            if index_file.exists() and self.metadata_path.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(index_file))
                
                # Load metadata
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                logger.info(f"✅ Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                # Create new index
                self.index = faiss.IndexFlatIP(self.dimension)
                self.metadata = []
                logger.info("🆕 Created new FAISS index")
                
        except Exception as e:
            logger.error(f"❌ Error loading FAISS index: {e}")
            # Create new index on error
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []
    
    def _save_index(self):
        """Save FAISS index to disk"""
        try:
            if self.index is None:
                return
            
            # Save FAISS index
            index_file = self.index_path / "faiss_index.bin"
            faiss.write_index(self.index, str(index_file))
            
            # Save metadata
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"💾 Saved FAISS index with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"❌ Error saving FAISS index: {e}")
    
    def add_vectors(
        self, 
        vectors: np.ndarray, 
        metadata_list: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Thêm vectors vào index
        
        Args:
            vectors: Array of vectors (numpy array)
            metadata_list: List of metadata for each vector
            
        Returns:
            List of vector IDs
        """
        try:
            if self.index is None:
                raise RuntimeError("FAISS index not initialized")
            
            if len(vectors) != len(metadata_list):
                raise ValueError("Number of vectors must match number of metadata")
            
            # Normalize vectors for cosine similarity
            faiss.normalize_L2(vectors)
            
            # Add to index
            start_id = self.index.ntotal
            self.index.add(vectors)
            
            # Generate vector IDs and add metadata
            vector_ids = []
            for i, metadata in enumerate(metadata_list):
                vector_id = f"vec_{start_id + i}"
                metadata["vector_id"] = vector_id
                metadata["index_id"] = start_id + i
                self.metadata.append(metadata)
                vector_ids.append(vector_id)
            
            # Save to disk
            self._save_index()
            
            logger.info(f"✅ Added {len(vectors)} vectors to FAISS index")
            return vector_ids
            
        except Exception as e:
            logger.error(f"❌ Error adding vectors: {e}")
            raise
    
    def search(
        self, 
        query_vector: np.ndarray, 
        k: int = 5,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm vectors tương tự
        
        Args:
            query_vector: Query vector (1D numpy array)
            k: Number of results to return
            document_id: Filter by document ID (optional)
            
        Returns:
            List of results with metadata and scores
        """
        try:
            if self.index is None or self.index.ntotal == 0:
                return []
            
            # Normalize query vector
            query_vector = query_vector.reshape(1, -1)
            faiss.normalize_L2(query_vector)
            
            # Search
            scores, indices = self.index.search(query_vector, min(k, self.index.ntotal))
            
            # Prepare results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # Invalid index
                    continue
                
                metadata = self.metadata[idx].copy()
                metadata["similarity_score"] = float(score)
                
                # Filter by document_id if specified
                if document_id and metadata.get("document_id") != document_id:
                    continue
                
                results.append(metadata)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching vectors: {e}")
            raise
    
    def get_vector_count(self) -> int:
        """Lấy số lượng vectors trong index"""
        return self.index.ntotal if self.index else 0
    
    def get_document_vectors(self, document_id: str) -> List[Dict[str, Any]]:
        """Lấy tất cả vectors của một document"""
        try:
            document_vectors = []
            for metadata in self.metadata:
                if metadata.get("document_id") == document_id:
                    document_vectors.append(metadata)
            
            return document_vectors
            
        except Exception as e:
            logger.error(f"❌ Error getting document vectors: {e}")
            raise
    
    def delete_document_vectors(self, document_id: str) -> int:
        """
        Xóa tất cả vectors của một document
        Note: FAISS không hỗ trợ xóa trực tiếp, cần rebuild index
        """
        try:
            # Find vectors to remove
            vectors_to_remove = []
            for i, metadata in enumerate(self.metadata):
                if metadata.get("document_id") == document_id:
                    vectors_to_remove.append(i)
            
            if not vectors_to_remove:
                return 0
            
            # Rebuild index without removed vectors
            new_metadata = []
            new_vectors = []
            
            for i, metadata in enumerate(self.metadata):
                if i not in vectors_to_remove:
                    new_metadata.append(metadata)
                    # Get vector from index
                    vector = self.index.reconstruct(i)
                    new_vectors.append(vector)
            
            # Create new index
            if new_vectors:
                new_vectors = np.array(new_vectors)
                self.index = faiss.IndexFlatIP(self.dimension)
                faiss.normalize_L2(new_vectors)
                self.index.add(new_vectors)
            else:
                self.index = faiss.IndexFlatIP(self.dimension)
            
            # Update metadata
            self.metadata = new_metadata
            
            # Save to disk
            self._save_index()
            
            logger.info(f"✅ Removed {len(vectors_to_remove)} vectors for document {document_id}")
            return len(vectors_to_remove)
            
        except Exception as e:
            logger.error(f"❌ Error deleting document vectors: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê về vector database"""
        try:
            stats = {
                "total_vectors": self.get_vector_count(),
                "dimension": self.dimension,
                "index_type": "IndexFlatIP",
                "documents_count": len(set(m.get("document_id") for m in self.metadata if m.get("document_id"))),
                "index_size_mb": self._get_index_size()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {}
    
    def _get_index_size(self) -> float:
        """Lấy kích thước index (MB)"""
        try:
            index_file = self.index_path / "faiss_index.bin"
            if index_file.exists():
                return index_file.stat().st_size / (1024 * 1024)
            return 0.0
        except:
            return 0.0
    
    def clear_all(self):
        """Xóa tất cả vectors"""
        try:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []
            self._save_index()
            logger.info("🗑️ Cleared all vectors from FAISS index")
        except Exception as e:
            logger.error(f"❌ Error clearing index: {e}")
            raise

# Global vector database instance
vector_db = VectorDB()
