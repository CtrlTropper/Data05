"""
PDF Processing Service
Xử lý PDF với OCR cho scan documents
"""

import os
import logging
import tempfile
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Service xử lý PDF với OCR"""
    
    def __init__(self):
        self.supported_languages = ['vie', 'eng']  # Vietnamese và English
        self.ocr_config = '--oem 3 --psm 6'  # OCR Engine Mode và Page Segmentation Mode
        self.is_initialized = False
        
    async def initialize(self):
        """Khởi tạo PDF processor"""
        try:
            # Kiểm tra tesseract có sẵn không
            tesseract_version = pytesseract.get_tesseract_version()
            logger.info(f"✅ Tesseract OCR version: {tesseract_version}")
            
            # Kiểm tra các ngôn ngữ có sẵn
            available_languages = pytesseract.get_languages()
            logger.info(f"📚 Available OCR languages: {available_languages}")
            
            # Kiểm tra ngôn ngữ cần thiết
            for lang in self.supported_languages:
                if lang in available_languages:
                    logger.info(f"✅ OCR language '{lang}' is available")
                else:
                    logger.warning(f"⚠️ OCR language '{lang}' is not available")
            
            self.is_initialized = True
            logger.info("✅ PDF Processor initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing PDF Processor: {e}")
            self.is_initialized = False
            raise
    
    def detect_pdf_type(self, pdf_path: str) -> str:
        """
        Phát hiện loại PDF (text-based hoặc image-based)
        
        Args:
            pdf_path: Đường dẫn đến file PDF
            
        Returns:
            str: 'text-based' hoặc 'image-based'
        """
        try:
            doc = fitz.open(pdf_path)
            text_content = ""
            
            # Lấy text từ 3 trang đầu để kiểm tra
            for page_num in range(min(3, len(doc))):
                page = doc[page_num]
                text_content += page.get_text()
            
            doc.close()
            
            # Nếu có ít text (dưới 50 ký tự) thì có thể là image-based
            if len(text_content.strip()) < 50:
                return 'image-based'
            else:
                return 'text-based'
                
        except Exception as e:
            logger.error(f"❌ Error detecting PDF type: {e}")
            return 'image-based'  # Default to image-based nếu có lỗi
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Trích xuất text từ PDF (text-based)
        
        Args:
            pdf_path: Đường dẫn đến file PDF
            
        Returns:
            Tuple[str, Dict]: (extracted_text, metadata)
        """
        try:
            doc = fitz.open(pdf_path)
            text_content = ""
            page_texts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                text_content += page_text + "\n"
                page_texts.append({
                    'page_number': page_num + 1,
                    'text': page_text,
                    'char_count': len(page_text)
                })
            
            doc.close()
            
            metadata = {
                'processing_type': 'text-based',
                'total_pages': len(page_texts),
                'total_characters': len(text_content),
                'page_details': page_texts,
                'ocr_language': None
            }
            
            logger.info(f"✅ Extracted text from {len(page_texts)} pages (text-based)")
            return text_content.strip(), metadata
            
        except Exception as e:
            logger.error(f"❌ Error extracting text from PDF: {e}")
            raise
    
    def extract_text_with_ocr(self, pdf_path: str, languages: List[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Trích xuất text từ PDF bằng OCR (image-based)
        
        Args:
            pdf_path: Đường dẫn đến file PDF
            languages: Danh sách ngôn ngữ OCR (default: ['vie', 'eng'])
            
        Returns:
            Tuple[str, Dict]: (extracted_text, metadata)
        """
        try:
            if languages is None:
                languages = self.supported_languages
            
            # Convert PDF to images
            logger.info(f"🔄 Converting PDF to images...")
            images = convert_from_path(
                pdf_path,
                dpi=300,  # High DPI for better OCR
                first_page=1,
                last_page=None,
                fmt='PNG'
            )
            
            text_content = ""
            page_texts = []
            ocr_language = '+'.join(languages)
            
            for page_num, image in enumerate(images):
                logger.info(f"🔍 Processing page {page_num + 1} with OCR...")
                
                # Preprocess image for better OCR
                processed_image = self._preprocess_image(image)
                
                # Extract text using OCR
                page_text = pytesseract.image_to_string(
                    processed_image,
                    lang=ocr_language,
                    config=self.ocr_config
                )
                
                text_content += page_text + "\n"
                page_texts.append({
                    'page_number': page_num + 1,
                    'text': page_text,
                    'char_count': len(page_text),
                    'image_size': image.size
                })
            
            metadata = {
                'processing_type': 'ocr-based',
                'total_pages': len(page_texts),
                'total_characters': len(text_content),
                'page_details': page_texts,
                'ocr_language': ocr_language,
                'ocr_config': self.ocr_config
            }
            
            logger.info(f"✅ Extracted text from {len(page_texts)} pages using OCR")
            return text_content.strip(), metadata
            
        except Exception as e:
            logger.error(f"❌ Error extracting text with OCR: {e}")
            raise
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Tiền xử lý ảnh để cải thiện chất lượng OCR
        
        Args:
            image: PIL Image object
            
        Returns:
            Image.Image: Processed image
        """
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Resize if too small (minimum 300px width)
            if image.width < 300:
                ratio = 300 / image.width
                new_height = int(image.height * ratio)
                image = image.resize((300, new_height), Image.Resampling.LANCZOS)
            
            # Apply some basic image enhancement
            # Note: Có thể thêm các kỹ thuật xử lý ảnh khác như:
            # - Noise reduction
            # - Contrast enhancement
            # - Binarization
            
            return image
            
        except Exception as e:
            logger.error(f"❌ Error preprocessing image: {e}")
            return image
    
    def process_pdf(self, pdf_path: str, force_ocr: bool = False) -> Tuple[str, Dict[str, Any]]:
        """
        Xử lý PDF file (tự động phát hiện loại hoặc force OCR)
        
        Args:
            pdf_path: Đường dẫn đến file PDF
            force_ocr: Bắt buộc sử dụng OCR (default: False)
            
        Returns:
            Tuple[str, Dict]: (extracted_text, metadata)
        """
        try:
            if not self.is_initialized:
                logger.warning("⚠️ PDF Processor not initialized, attempting to initialize...")
                import asyncio
                asyncio.create_task(self.initialize())
            
            # Phát hiện loại PDF
            if force_ocr:
                pdf_type = 'image-based'
                logger.info("🔄 Force OCR mode enabled")
            else:
                pdf_type = self.detect_pdf_type(pdf_path)
                logger.info(f"🔍 Detected PDF type: {pdf_type}")
            
            # Xử lý theo loại PDF
            if pdf_type == 'text-based':
                return self.extract_text_from_pdf(pdf_path)
            else:
                return self.extract_text_with_ocr(pdf_path)
                
        except Exception as e:
            logger.error(f"❌ Error processing PDF: {e}")
            # Fallback: thử OCR nếu text extraction thất bại
            try:
                logger.info("🔄 Attempting OCR as fallback...")
                return self.extract_text_with_ocr(pdf_path)
            except Exception as ocr_error:
                logger.error(f"❌ OCR fallback also failed: {ocr_error}")
                raise
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê về PDF processing
        
        Returns:
            Dict[str, Any]: Processing statistics
        """
        return {
            'initialized': self.is_initialized,
            'supported_languages': self.supported_languages,
            'ocr_config': self.ocr_config,
            'tesseract_version': pytesseract.get_tesseract_version() if self.is_initialized else None,
            'available_languages': pytesseract.get_languages() if self.is_initialized else []
        }

# Global PDF processor instance
pdf_processor = PDFProcessor()
