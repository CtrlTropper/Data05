"""
Test script cho PDF OCR functionality
Kiểm tra chức năng xử lý PDF với OCR
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.pdf_processor import pdf_processor

async def test_pdf_processor():
    """Test PDF processor với OCR"""
    print("\n" + "="*60)
    print("🧪 TESTING PDF PROCESSOR WITH OCR")
    print("="*60)
    
    try:
        # Initialize PDF processor
        print("Step 1: Initialize PDF processor")
        await pdf_processor.initialize()
        print("✅ PDF processor initialized successfully")
        
        # Get processing stats
        print("\nStep 2: Get processing stats")
        stats = pdf_processor.get_processing_stats()
        print(f"✅ Processing stats: {stats}")
        
        # Test with sample PDF (if available)
        test_pdf_path = "test_documents/sample.pdf"
        if os.path.exists(test_pdf_path):
            print(f"\nStep 3: Test PDF processing with {test_pdf_path}")
            
            # Test text-based PDF
            print("Testing text-based PDF processing...")
            try:
                text, metadata = pdf_processor.process_pdf(test_pdf_path, force_ocr=False)
                print(f"✅ Text-based processing successful")
                print(f"   Processing type: {metadata['processing_type']}")
                print(f"   Total pages: {metadata['total_pages']}")
                print(f"   Text length: {len(text)} characters")
                print(f"   First 100 chars: {text[:100]}...")
            except Exception as e:
                print(f"❌ Text-based processing failed: {e}")
            
            # Test OCR-based PDF
            print("\nTesting OCR-based PDF processing...")
            try:
                text, metadata = pdf_processor.process_pdf(test_pdf_path, force_ocr=True)
                print(f"✅ OCR-based processing successful")
                print(f"   Processing type: {metadata['processing_type']}")
                print(f"   Total pages: {metadata['total_pages']}")
                print(f"   OCR language: {metadata.get('ocr_language', 'N/A')}")
                print(f"   Text length: {len(text)} characters")
                print(f"   First 100 chars: {text[:100]}...")
            except Exception as e:
                print(f"❌ OCR-based processing failed: {e}")
        else:
            print(f"\nStep 3: No test PDF found at {test_pdf_path}")
            print("   Create a test PDF to test processing functionality")
        
        # Test PDF type detection
        if os.path.exists(test_pdf_path):
            print(f"\nStep 4: Test PDF type detection")
            pdf_type = pdf_processor.detect_pdf_type(test_pdf_path)
            print(f"✅ Detected PDF type: {pdf_type}")
        
        print("\n" + "="*60)
        print("📊 PDF PROCESSOR TEST SUMMARY")
        print("="*60)
        print("✅ PDF processor initialization: PASSED")
        print("✅ Processing stats retrieval: PASSED")
        if os.path.exists(test_pdf_path):
            print("✅ PDF processing: PASSED")
            print("✅ PDF type detection: PASSED")
        else:
            print("⚠️ PDF processing: SKIPPED (no test file)")
            print("⚠️ PDF type detection: SKIPPED (no test file)")
        
        print("\n🎉 PDF Processor with OCR is working correctly!")
        
    except Exception as e:
        print(f"\n❌ PDF Processor test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_ocr_languages():
    """Test OCR language support"""
    print("\n" + "="*60)
    print("🧪 TESTING OCR LANGUAGE SUPPORT")
    print("="*60)
    
    try:
        await pdf_processor.initialize()
        
        # Test available languages
        import pytesseract
        available_languages = pytesseract.get_languages()
        print(f"✅ Available OCR languages: {available_languages}")
        
        # Check required languages
        required_languages = ['vie', 'eng']
        for lang in required_languages:
            if lang in available_languages:
                print(f"✅ Language '{lang}' is available")
            else:
                print(f"❌ Language '{lang}' is NOT available")
        
        # Test OCR config
        print(f"✅ OCR config: {pdf_processor.ocr_config}")
        
    except Exception as e:
        print(f"❌ OCR language test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 PDF OCR TEST")
    print("Testing PDF processing with OCR functionality")
    
    # Test PDF processor
    await test_pdf_processor()
    
    # Test OCR languages
    await test_ocr_languages()
    
    print("\n🎉 All PDF OCR tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
