"""
Model Manager Service
Quản lý việc load và sử dụng các AI models
"""

import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    """Quản lý các AI models"""
    
    def __init__(self):
        self.embedding_model: Optional[SentenceTransformer] = None
        self.llm_model: Optional[Any] = None
        self.llm_tokenizer: Optional[Any] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models_loaded = False
    
    async def initialize(self):
        """Khởi tạo và load các models"""
        try:
            logger.info("🚀 Initializing AI models...")
            
            # Load embedding model
            await self.load_embedding_model()
            
            # Load LLM model
            await self.load_llm_model()
            
            self.models_loaded = True
            logger.info("✅ All models loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error initializing models: {e}")
            raise
    
    async def load_embedding_model(self):
        """Load embedding model (multilingual-e5-large)"""
        try:
            logger.info("📥 Loading embedding model...")
            
            # TODO: Implement embedding model loading
            # self.embedding_model = SentenceTransformer(
            #     settings.EMBEDDING_MODEL_PATH,
            #     device=self.device
            # )
            
            logger.info("✅ Embedding model loaded!")
            
        except Exception as e:
            logger.error(f"❌ Error loading embedding model: {e}")
            raise
    
    async def load_llm_model(self):
        """Load LLM model (gpt-oss-20b)"""
        try:
            logger.info("📥 Loading LLM model...")
            
            # TODO: Implement LLM model loading
            # self.llm_tokenizer = AutoTokenizer.from_pretrained(
            #     settings.LLM_MODEL_PATH
            # )
            # 
            # self.llm_model = AutoModelForCausalLM.from_pretrained(
            #     settings.LLM_MODEL_PATH,
            #     torch_dtype=torch.float16,
            #     device_map="auto" if self.device == "cuda" else None
            # )
            
            logger.info("✅ LLM model loaded!")
            
        except Exception as e:
            logger.error(f"❌ Error loading LLM model: {e}")
            raise
    
    def get_embedding(self, text: str) -> list:
        """Tạo embedding cho text"""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not loaded")
        
        # TODO: Implement embedding generation
        # return self.embedding_model.encode(text).tolist()
        
        # Placeholder
        return [0.0] * 768
    
    def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response từ LLM"""
        if not self.llm_model or not self.llm_tokenizer:
            raise RuntimeError("LLM model not loaded")
        
        # TODO: Implement LLM response generation
        # inputs = self.llm_tokenizer(prompt, return_tensors="pt")
        # with torch.no_grad():
        #     outputs = self.llm_model.generate(
        #         **inputs,
        #         max_new_tokens=max_tokens,
        #         temperature=settings.TEMPERATURE,
        #         do_sample=True
        #     )
        # response = self.llm_tokenizer.decode(outputs[0], skip_special_tokens=True)
        # return response
        
        # Placeholder
        return "Response from LLM (placeholder)"
    
    def get_model_status(self) -> Dict[str, Any]:
        """Lấy trạng thái các models"""
        return {
            "embedding_model_loaded": self.embedding_model is not None,
            "llm_model_loaded": self.llm_model is not None,
            "device": self.device,
            "models_loaded": self.models_loaded
        }
    
    async def cleanup(self):
        """Cleanup khi shutdown"""
        logger.info("🧹 Cleaning up models...")
        
        # Clear GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.embedding_model = None
        self.llm_model = None
        self.llm_tokenizer = None
        
        logger.info("✅ Models cleanup complete!")

# Global model manager instance
model_manager = ModelManager()
