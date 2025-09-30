"""
Embedding Service - Offline Embedding với multilingual-e5-large
Service xử lý embedding hoàn toàn offline
"""

import os
import logging
import numpy as np
from typing import List, Union, Optional
import torch
from sentence_transformers import SentenceTransformer
import pickle
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_path: str = "models/embedding"):
        """
        Khởi tạo Embedding Service
        
        Args:
            model_path: Đường dẫn đến thư mục chứa model offline
        """
        self.model_path = model_path
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "intfloat/multilingual-e5-large"
        self.dimension = 1024  # Dimension của multilingual-e5-large
        self.is_loaded = False
        
        logger.info(f"Embedding Service initialized. Device: {self.device}")
        logger.info(f"Model path: {self.model_path}")

    async def load_model(self):
        """
        Load model embedding từ thư mục offline
        """
        if self.is_loaded:
            logger.info("Model already loaded")
            return

        try:
            logger.info(f"⏳ Loading embedding model from {self.model_path}...")
            
            # Kiểm tra thư mục model
            if not os.path.exists(self.model_path):
                logger.error(f"❌ Model path not found: {self.model_path}")
                raise FileNotFoundError(f"Embedding model not found at {self.model_path}. Please download it first.")

            # Load model với local_files_only=True để đảm bảo offline
            self.model = SentenceTransformer(
                self.model_path,
                device=self.device,
                local_files_only=True  # Quan trọng: chỉ load từ local
            )
            
            self.is_loaded = True
            logger.info(f"✅ Embedding model loaded successfully on {self.device}")
            logger.info(f"Model dimension: {self.dimension}")
            
        except Exception as e:
            logger.error(f"❌ Error loading embedding model: {e}")
            self.model = None
            self.is_loaded = False
            raise

    async def cleanup(self):
        """
        Giải phóng tài nguyên model
        """
        logger.info("🧹 Cleaning up embedding model resources...")
        if self.model is not None:
            del self.model
            torch.cuda.empty_cache()
        self.model = None
        self.is_loaded = False
        logger.info("✅ Embedding model resources cleaned up")

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Tạo embedding cho một đoạn text
        
        Args:
            text: Đoạn text cần tạo embedding
            
        Returns:
            np.ndarray: Vector embedding
        """
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Model not loaded. Please call load_model() first.")

        try:
            # Preprocess text cho E5 model
            processed_text = self._preprocess_text(text)
            
            # Tạo embedding
            embedding = self.model.encode(
                processed_text,
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=1
            )
            
            # Đảm bảo embedding là 1D array
            if embedding.ndim > 1:
                embedding = embedding.flatten()
            
            logger.debug(f"Generated embedding for text: {text[:50]}...")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Tạo embeddings cho nhiều đoạn text cùng lúc
        
        Args:
            texts: Danh sách các đoạn text
            
        Returns:
            np.ndarray: Ma trận embeddings (n_texts, dimension)
        """
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Model not loaded. Please call load_model() first.")

        try:
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            # Tạo embeddings batch
            embeddings = self.model.encode(
                processed_texts,
                convert_to_numpy=True,
                show_progress_bar=True,
                batch_size=8
            )
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Error generating batch embeddings: {e}")
            raise

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text cho E5 model
        E5 model cần prefix để hiểu context
        """
        if not text.strip():
            return "query: " + text
        
        # Thêm prefix cho query (có thể customize cho retrieval)
        return "query: " + text.strip()

    def get_embedding_dimension(self) -> int:
        """
        Lấy dimension của embedding
        """
        return self.dimension

    def get_model_info(self) -> dict:
        """
        Lấy thông tin về model
        """
        return {
            "model_name": self.model_name,
            "model_path": self.model_path,
            "loaded": self.is_loaded,
            "device": self.device,
            "dimension": self.dimension,
            "model_loaded": self.model is not None
        }

    def validate_embedding(self, embedding: np.ndarray) -> bool:
        """
        Validate embedding vector
        """
        if not isinstance(embedding, np.ndarray):
            return False
        
        if embedding.ndim != 1:
            return False
            
        if embedding.shape[0] != self.dimension:
            return False
            
        if np.isnan(embedding).any() or np.isinf(embedding).any():
            return False
            
        return True

    def normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """
        Normalize embedding vector
        """
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm

    def save_embeddings(self, embeddings: np.ndarray, metadata: List[dict], filepath: str):
        """
        Lưu embeddings và metadata ra file
        """
        try:
            data = {
                "embeddings": embeddings,
                "metadata": metadata,
                "dimension": self.dimension,
                "model_name": self.model_name
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
                
            logger.info(f"Saved embeddings to {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error saving embeddings: {e}")
            raise

    def load_embeddings(self, filepath: str) -> tuple:
        """
        Load embeddings và metadata từ file
        """
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                
            embeddings = data["embeddings"]
            metadata = data["metadata"]
            
            logger.info(f"Loaded embeddings from {filepath}")
            return embeddings, metadata
            
        except Exception as e:
            logger.error(f"❌ Error loading embeddings: {e}")
            raise

# Global instance
embedding_service = EmbeddingService()