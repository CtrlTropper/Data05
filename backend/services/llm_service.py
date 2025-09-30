"""
LLM Service - Offline LLM với gpt-oss-20b
Service xử lý LLM hoàn toàn offline từ local GPU
"""

import os
import torch
import asyncio
import gc
import warnings
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    GenerationConfig,
    BitsAndBytesConfig
)
from typing import List, Dict, Any, Optional, AsyncGenerator
import logging
from pathlib import Path

# Suppress warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

class LLMService:
    """Service xử lý LLM offline với GPU optimization"""
    
    def __init__(self, model_path: str = "models/llm"):
        self.model_path = model_path
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False
        self.model_name = "gpt-oss-20b"
        self.max_length = 4096  # Max context length
        
        # GPU optimization settings
        self.use_quantization = True
        self.load_in_8bit = True
        self.load_in_4bit = False
        
        # Generation config
        self.generation_config = GenerationConfig(
            max_new_tokens=1000,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            do_sample=True,
            pad_token_id=None,
            eos_token_id=None,
            repetition_penalty=1.1,
            length_penalty=1.0,
            early_stopping=True,
            use_cache=True
        )
        
        # Ensure model directory exists
        Path(model_path).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"LLM Service initialized. Device: {self.device}")
        logger.info(f"Model path: {self.model_path}")
        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    async def load_model(self):
        """Load LLM model từ thư mục local với GPU optimization"""
        try:
            logger.info("📥 Loading LLM model...")
            
            # Check if model exists locally
            if not os.path.exists(self.model_path):
                logger.error(f"❌ Model path not found: {self.model_path}")
                raise FileNotFoundError(f"Model path not found: {self.model_path}")
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True,
                trust_remote_code=True,
                use_fast=True
            )
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
            
            # Configure quantization for GPU
            quantization_config = None
            if self.device == "cuda" and self.use_quantization:
                if self.load_in_4bit:
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
                    logger.info("Using 4-bit quantization")
                elif self.load_in_8bit:
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True
                    )
                    logger.info("Using 8-bit quantization")
            
            # Load model với cấu hình tối ưu cho GPU
            logger.info("Loading model...")
            model_kwargs = {
                "local_files_only": True,
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "low_cpu_mem_usage": True,
            }
            
            if self.device == "cuda":
                if quantization_config:
                    model_kwargs["quantization_config"] = quantization_config
                    model_kwargs["device_map"] = "auto"
                else:
                    model_kwargs["device_map"] = "auto"
            else:
                model_kwargs["device_map"] = None
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                **model_kwargs
            )
            
            # Move to device if not using device_map
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            # Enable evaluation mode
            self.model.eval()
            
            # Update generation config with tokenizer info
            self.generation_config.pad_token_id = self.tokenizer.pad_token_id
            self.generation_config.eos_token_id = self.tokenizer.eos_token_id
            
            self.model_loaded = True
            logger.info(f"✅ LLM model '{self.model_name}' loaded from {self.model_path}")
            logger.info(f"🔧 Device: {self.device}")
            logger.info(f"📏 Model type: {type(self.model).__name__}")
            
            # Log memory usage
            if torch.cuda.is_available():
                memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
                memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
                logger.info(f"GPU Memory - Allocated: {memory_allocated:.1f} GB, Reserved: {memory_reserved:.1f} GB")
            
        except Exception as e:
            logger.error(f"❌ Error loading LLM model: {e}")
            raise
    
    def generate_answer(self, question: str, context: str = "", max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Tạo câu trả lời từ question và context - Luôn trả lời bằng tiếng Việt
        
        Args:
            question: Câu hỏi của user
            context: Context từ RAG search
            max_tokens: Số token tối đa
            temperature: Độ ngẫu nhiên
            
        Returns:
            str: Câu trả lời từ LLM (luôn bằng tiếng Việt)
        """
        try:
            if not self.model_loaded or self.model is None or self.tokenizer is None:
                raise RuntimeError("LLM model not loaded")
            
            if not question or not question.strip():
                raise ValueError("Question cannot be empty")
            
            # Detect language and translate if needed
            question_vi, context_vi = self._ensure_vietnamese_input(question.strip(), context.strip())
            
            # Create prompt
            prompt = self._create_prompt(question_vi, context_vi)
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length - max_tokens,
                padding=True,
                add_special_tokens=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Update generation config
            generation_config = GenerationConfig(
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                top_k=50,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1,
                no_repeat_ngram_size=3,
                early_stopping=True,
                use_cache=True
            )
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    generation_config=generation_config,
                    do_sample=True
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],  # Skip input tokens
                skip_special_tokens=True
            )
            
            # Clean response
            response = self._clean_response(response)
            
            # Ensure response is in Vietnamese
            response = self._ensure_vietnamese_output(response)
            
            logger.info(f"✅ Generated answer for question: {question[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating answer: {e}")
            return "Xin lỗi, tôi không thể tạo câu trả lời lúc này."
    
    def _create_prompt(self, question: str, context: str = "") -> str:
        """
        Tạo prompt cho LLM - Luôn yêu cầu trả lời bằng tiếng Việt
        
        Args:
            question: Câu hỏi
            context: Context từ RAG
            
        Returns:
            str: Prompt hoàn chỉnh
        """
        if context and context.strip():
            prompt = f"""Dựa trên thông tin sau:

Context: {context.strip()}

Hãy trả lời câu hỏi sau một cách ngắn gọn và chính xác bằng tiếng Việt, chỉ sử dụng thông tin được cung cấp:

Câu hỏi: {question.strip()}

Trả lời (bằng tiếng Việt):"""
        else:
            prompt = f"""Hãy trả lời câu hỏi sau một cách ngắn gọn và chính xác bằng tiếng Việt:

Câu hỏi: {question.strip()}

Trả lời (bằng tiếng Việt):"""
        
        return prompt

    def _clean_response(self, response: str) -> str:
        """
        Làm sạch response từ LLM
        
        Args:
            response: Response thô từ LLM
            
        Returns:
            str: Response đã được làm sạch
        """
        # Remove common artifacts
        response = response.strip()
        
        # Remove repeated phrases
        lines = response.split('\n')
        cleaned_lines = []
        seen = set()
        
        for line in lines:
            line = line.strip()
            if line and line not in seen:
                cleaned_lines.append(line)
                seen.add(line)
        
        response = '\n'.join(cleaned_lines)
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Trả lời:",
            "Câu trả lời:",
            "Answer:",
            "Response:",
        ]
        
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        return response

    def _ensure_vietnamese_input(self, question: str, context: str) -> tuple[str, str]:
        """
        Đảm bảo input (question và context) là tiếng Việt
        
        Args:
            question: Câu hỏi gốc
            context: Context gốc
            
        Returns:
            tuple: (question_vi, context_vi) - Câu hỏi và context đã được dịch sang tiếng Việt
        """
        try:
            # Detect if question is in English
            if self._is_english(question):
                logger.info(f"🔄 Translating English question to Vietnamese: {question[:50]}...")
                question_vi = self._translate_to_vietnamese(question)
            else:
                question_vi = question
            
            # Detect if context is in English
            if context and self._is_english(context):
                logger.info(f"🔄 Translating English context to Vietnamese...")
                context_vi = self._translate_to_vietnamese(context)
            else:
                context_vi = context
            
            return question_vi, context_vi
            
        except Exception as e:
            logger.error(f"❌ Error ensuring Vietnamese input: {e}")
            # Return original if translation fails
            return question, context

    def _ensure_vietnamese_output(self, response: str) -> str:
        """
        Đảm bảo output là tiếng Việt
        
        Args:
            response: Response gốc từ LLM
            
        Returns:
            str: Response đã được đảm bảo là tiếng Việt
        """
        try:
            # Check if response is in English
            if self._is_english(response):
                logger.info(f"🔄 Translating English response to Vietnamese...")
                response_vi = self._translate_to_vietnamese(response)
                return response_vi
            else:
                return response
                
        except Exception as e:
            logger.error(f"❌ Error ensuring Vietnamese output: {e}")
            # Return original if translation fails
            return response

    def _is_english(self, text: str) -> bool:
        """
        Kiểm tra xem text có phải là tiếng Anh không
        
        Args:
            text: Text cần kiểm tra
            
        Returns:
            bool: True nếu là tiếng Anh, False nếu không
        """
        if not text or not text.strip():
            return False
        
        # Vietnamese characters
        vietnamese_chars = set('àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ')
        
        # Count Vietnamese characters
        vietnamese_count = sum(1 for char in text.lower() if char in vietnamese_chars)
        
        # Count total alphabetic characters
        total_alpha = sum(1 for char in text if char.isalpha())
        
        # If more than 10% Vietnamese characters, consider it Vietnamese
        if total_alpha > 0 and vietnamese_count / total_alpha > 0.1:
            return False
        
        # Check for common English words
        english_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'can', 'cannot', 'this', 'that', 'these', 'those', 'a', 'an', 'as', 'if',
            'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose'
        }
        
        words = text.lower().split()
        english_word_count = sum(1 for word in words if word in english_words)
        
        # If more than 20% English words, consider it English
        if len(words) > 0 and english_word_count / len(words) > 0.2:
            return True
        
        return False

    def _translate_to_vietnamese(self, text: str) -> str:
        """
        Dịch text sang tiếng Việt sử dụng LLM
        
        Args:
            text: Text cần dịch
            
        Returns:
            str: Text đã được dịch sang tiếng Việt
        """
        try:
            if not self.model_loaded or self.model is None or self.tokenizer is None:
                logger.warning("LLM model not loaded, returning original text")
                return text
            
            # Create translation prompt
            translation_prompt = f"""Hãy dịch đoạn text sau sang tiếng Việt một cách tự nhiên và chính xác:

Text cần dịch: {text}

Bản dịch tiếng Việt:"""
            
            # Tokenize input
            inputs = self.tokenizer(
                translation_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length - 200,  # Reserve tokens for response
                padding=True,
                add_special_tokens=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate translation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.3,  # Lower temperature for more consistent translation
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    no_repeat_ngram_size=3,
                    early_stopping=True,
                    use_cache=True
                )
            
            # Decode translation
            translation = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],  # Skip input tokens
                skip_special_tokens=True
            ).strip()
            
            # Clean translation
            translation = self._clean_response(translation)
            
            logger.info(f"✅ Translated: {text[:30]}... -> {translation[:30]}...")
            return translation
            
        except Exception as e:
            logger.error(f"❌ Error translating to Vietnamese: {e}")
            return text  # Return original if translation fails
    
    async def generate_answer_with_streaming(self, question: str, context: str = "", max_tokens: int = 1000, temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """
        Tạo câu trả lời với streaming (async generator) - Luôn trả lời bằng tiếng Việt
        
        Args:
            question: Câu hỏi của user
            context: Context từ RAG search
            max_tokens: Số token tối đa
            temperature: Độ ngẫu nhiên
            
        Yields:
            str: Từng phần của câu trả lời (luôn bằng tiếng Việt)
        """
        try:
            if not self.model_loaded or self.model is None or self.tokenizer is None:
                raise RuntimeError("LLM model not loaded")
            
            # Detect language and translate if needed
            question_vi, context_vi = self._ensure_vietnamese_input(question.strip(), context.strip())
            
            # Create prompt
            prompt = self._create_prompt(question_vi, context_vi)
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length - max_tokens,
                padding=True,
                add_special_tokens=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate with streaming
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    no_repeat_ngram_size=3,
                    early_stopping=True,
                    use_cache=True
                )
                
                # Decode full response
                response = self.tokenizer.decode(
                    outputs[0][inputs['input_ids'].shape[1]:],
                    skip_special_tokens=True
                ).strip()
                
                # Clean response
                response = self._clean_response(response)
                
                # Ensure response is in Vietnamese
                response = self._ensure_vietnamese_output(response)
                
                # Yield response in chunks for streaming effect
                words = response.split()
                for i, word in enumerate(words):
                    if i == len(words) - 1:
                        yield word
                    else:
                        yield word + " "
                    # Small delay for streaming effect
                    await asyncio.sleep(0.05)
            
        except Exception as e:
            logger.error(f"❌ Error in streaming generation: {e}")
            yield "Xin lỗi, tôi không thể tạo câu trả lời lúc này."
    
    def get_model_info(self) -> Dict[str, Any]:
        """Lấy thông tin về model"""
        info = {
            "model_loaded": self.model_loaded,
            "model_path": self.model_path,
            "device": self.device,
            "model_name": self.model_name,
            "max_length": self.max_length,
            "use_quantization": self.use_quantization,
            "load_in_8bit": self.load_in_8bit,
            "load_in_4bit": self.load_in_4bit,
            "generation_config": {
                "max_new_tokens": self.generation_config.max_new_tokens,
                "temperature": self.generation_config.temperature,
                "top_p": self.generation_config.top_p,
                "top_k": self.generation_config.top_k
            }
        }
        
        # Add GPU info
        if torch.cuda.is_available():
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory_total"] = torch.cuda.get_device_properties(0).total_memory / 1024**3
            info["gpu_memory_allocated"] = torch.cuda.memory_allocated(0) / 1024**3
            info["gpu_memory_reserved"] = torch.cuda.memory_reserved(0) / 1024**3
        
        return info
    
    def update_generation_config(self, **kwargs):
        """Cập nhật generation config"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.generation_config, key):
                    setattr(self.generation_config, key, value)
                    logger.info(f"✅ Updated generation config: {key} = {value}")
                else:
                    logger.warning(f"⚠️ Unknown generation config parameter: {key}")
        except Exception as e:
            logger.error(f"❌ Error updating generation config: {e}")
            raise

    def optimize_for_gpu(self, use_quantization: bool = True, load_in_8bit: bool = True, load_in_4bit: bool = False):
        """
        Cấu hình tối ưu cho GPU
        
        Args:
            use_quantization: Sử dụng quantization
            load_in_8bit: Load model với 8-bit
            load_in_4bit: Load model với 4-bit
        """
        if self.model_loaded:
            logger.warning("Cannot change GPU optimization after model is loaded")
            return
        
        self.use_quantization = use_quantization
        self.load_in_8bit = load_in_8bit
        self.load_in_4bit = load_in_4bit
        
        logger.info(f"GPU optimization settings updated: quantization={use_quantization}, 8bit={load_in_8bit}, 4bit={load_in_4bit}")

    def clear_gpu_cache(self):
        """
        Xóa GPU cache
        """
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            gc.collect()
            logger.info("GPU cache cleared")
    
    async def cleanup(self):
        """Cleanup khi shutdown"""
        logger.info("🧹 Cleaning up LLM service...")
        
        # Clear GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            gc.collect()
        
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        
        logger.info("✅ LLM service cleanup complete!")

# Global LLM service instance
llm_service = LLMService()
