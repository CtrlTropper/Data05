"""
Test script cho Vietnamese Translation
Kiểm tra chức năng dịch và đảm bảo output luôn là tiếng Việt
"""

import asyncio
import httpx
import time
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def test_vietnamese_translation():
    """Test Vietnamese translation functionality"""
    print("\n" + "="*60)
    print("🧪 TESTING VIETNAMESE TRANSLATION")
    print("="*60)
    
    # Test cases
    test_cases = [
        # Vietnamese questions (should remain in Vietnamese)
        {
            "question": "Bảo mật thông tin là gì?",
            "expected_language": "Vietnamese",
            "category": "Vietnamese Security Question"
        },
        {
            "question": "Làm thế nào để bảo vệ khỏi ransomware?",
            "expected_language": "Vietnamese",
            "category": "Vietnamese Security Question"
        },
        {
            "question": "SOC hoạt động như thế nào?",
            "expected_language": "Vietnamese",
            "category": "Vietnamese Security Question"
        },
        
        # English questions (should be translated to Vietnamese)
        {
            "question": "What is information security?",
            "expected_language": "Vietnamese",
            "category": "English Security Question"
        },
        {
            "question": "How to protect against ransomware?",
            "expected_language": "Vietnamese",
            "category": "English Security Question"
        },
        {
            "question": "How does SOC work?",
            "expected_language": "Vietnamese",
            "category": "English Security Question"
        },
        {
            "question": "What is penetration testing?",
            "expected_language": "Vietnamese",
            "category": "English Security Question"
        },
        {
            "question": "Explain network security best practices",
            "expected_language": "Vietnamese",
            "category": "English Security Question"
        },
        {
            "question": "What are the OWASP Top 10 vulnerabilities?",
            "expected_language": "Vietnamese",
            "category": "English Security Question"
        },
        {
            "question": "How to implement ISO 27001?",
            "expected_language": "Vietnamese",
            "category": "English Security Question"
        }
    ]
    
    # Test chat endpoint
    print("Testing /api/chat endpoint with Vietnamese translation...\n")
    
    passed = 0
    total = len(test_cases)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, test_case in enumerate(test_cases, 1):
            question = test_case["question"]
            expected_language = test_case["expected_language"]
            category = test_case["category"]
            
            try:
                # Send chat request
                response = await client.post(
                    "http://localhost:8000/api/chat",
                    json={
                        "question": question,
                        "top_k": 3
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response", "")
                    
                    # Check if response is in Vietnamese
                    is_vietnamese = _is_vietnamese_text(response_text)
                    
                    # Check if response is rejection message
                    is_rejection = "Xin lỗi, tôi chỉ hỗ trợ các câu hỏi liên quan đến An ninh An toàn thông tin" in response_text
                    
                    # Determine if test passed
                    if expected_language == "Vietnamese" and is_vietnamese and not is_rejection:
                        status = "✅ PASS"
                        passed += 1
                    else:
                        status = "❌ FAIL"
                    
                    print(f"Test {i:2d}: {status}")
                    print(f"  Question: {question}")
                    print(f"  Category: {category}")
                    print(f"  Expected: {expected_language}")
                    print(f"  Is Vietnamese: {is_vietnamese}")
                    print(f"  Is Rejection: {is_rejection}")
                    print(f"  Response: {response_text[:100]}...")
                    print()
                    
                else:
                    print(f"Test {i:2d}: ❌ FAIL - HTTP {response.status_code}")
                    print(f"  Question: {question}")
                    print(f"  Error: {response.text}")
                    print()
                    
            except Exception as e:
                print(f"Test {i:2d}: ❌ ERROR - {e}")
                print(f"  Question: {question}")
                print()
    
    return passed, total

async def test_streaming_vietnamese_translation():
    """Test streaming Vietnamese translation"""
    print("\n" + "="*60)
    print("🧪 TESTING STREAMING VIETNAMESE TRANSLATION")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "question": "What is cybersecurity?",
            "expected_language": "Vietnamese",
            "category": "English Security Question"
        },
        {
            "question": "Bảo mật mạng là gì?",
            "expected_language": "Vietnamese",
            "category": "Vietnamese Security Question"
        }
    ]
    
    print("Testing /api/chat/stream endpoint with Vietnamese translation...\n")
    
    async with httpx.AsyncClient(timeout=None) as client:
        for i, test_case in enumerate(test_cases, 1):
            question = test_case["question"]
            expected_language = test_case["expected_language"]
            category = test_case["category"]
            
            try:
                # Send streaming chat request
                response = await client.post(
                    "http://localhost:8000/api/chat/stream",
                    json={
                        "question": question,
                        "top_k": 3
                    },
                    headers={"Accept": "text/event-stream"}
                )
                
                if response.status_code == 200:
                    print(f"Test {i}: Streaming chat started")
                    print(f"  Question: {question}")
                    print(f"  Category: {category}")
                    print(f"  Expected: {expected_language}")
                    
                    # Read streaming response
                    full_response = ""
                    rejection_detected = False
                    
                    async for chunk in response.aiter_bytes():
                        try:
                            decoded_chunk = chunk.decode('utf-8')
                            for line in decoded_chunk.split('\n'):
                                if line.startswith("data: "):
                                    import json
                                    data = json.loads(line[len("data: "):])
                                    
                                    if data["type"] == "token":
                                        full_response += data["content"]
                                        
                                        # Check for rejection message
                                        if "Xin lỗi, tôi chỉ hỗ trợ" in full_response:
                                            rejection_detected = True
                                            break
                                    
                                    elif data["type"] == "end":
                                        break
                                    
                                    elif data["type"] == "error":
                                        print(f"  Error: {data['message']}")
                                        break
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            print(f"  Stream error: {e}")
                            break
                    
                    # Check if response is in Vietnamese
                    is_vietnamese = _is_vietnamese_text(full_response)
                    
                    # Check result
                    if expected_language == "Vietnamese" and is_vietnamese and not rejection_detected:
                        status = "✅ PASS"
                    else:
                        status = "❌ FAIL"
                    
                    print(f"  Status: {status}")
                    print(f"  Is Vietnamese: {is_vietnamese}")
                    print(f"  Rejection detected: {rejection_detected}")
                    print(f"  Response length: {len(full_response)} chars")
                    print(f"  Response: {full_response[:100]}...")
                    print()
                    
                else:
                    print(f"Test {i}: ❌ FAIL - HTTP {response.status_code}")
                    print(f"  Question: {question}")
                    print()
                    
            except Exception as e:
                print(f"Test {i}: ❌ ERROR - {e}")
                print(f"  Question: {question}")
                print()

def _is_vietnamese_text(text: str) -> bool:
    """
    Kiểm tra xem text có phải là tiếng Việt không
    
    Args:
        text: Text cần kiểm tra
        
    Returns:
        bool: True nếu là tiếng Việt, False nếu không
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
        return True
    
    # Check for common Vietnamese words
    vietnamese_words = {
        'là', 'của', 'và', 'trong', 'với', 'được', 'có', 'không', 'để', 'từ',
        'này', 'đó', 'như', 'khi', 'nếu', 'thì', 'sẽ', 'đã', 'đang', 'sẽ',
        'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười',
        'tôi', 'bạn', 'anh', 'chị', 'em', 'chúng', 'họ', 'chúng tôi', 'chúng ta',
        'gì', 'nào', 'đâu', 'sao', 'tại sao', 'như thế nào', 'bao nhiêu',
        'bảo mật', 'an toàn', 'thông tin', 'mạng', 'hệ thống', 'dữ liệu',
        'tấn công', 'bảo vệ', 'phòng chống', 'kiểm tra', 'đánh giá'
    }
    
    words = text.lower().split()
    vietnamese_word_count = sum(1 for word in words if word in vietnamese_words)
    
    # If more than 20% Vietnamese words, consider it Vietnamese
    if len(words) > 0 and vietnamese_word_count / len(words) > 0.2:
        return True
    
    return False

async def test_language_detection():
    """Test language detection functionality"""
    print("\n" + "="*60)
    print("🧪 TESTING LANGUAGE DETECTION")
    print("="*60)
    
    # Test cases
    test_cases = [
        ("Bảo mật thông tin là gì?", "Vietnamese"),
        ("What is information security?", "English"),
        ("Làm thế nào để bảo vệ khỏi ransomware?", "Vietnamese"),
        ("How to protect against ransomware?", "English"),
        ("SOC hoạt động như thế nào?", "Vietnamese"),
        ("How does SOC work?", "English"),
        ("Tấn công mạng có những loại nào?", "Vietnamese"),
        ("What are the types of cyber attacks?", "English"),
        ("Mã hóa dữ liệu quan trọng như thế nào?", "Vietnamese"),
        ("How important is data encryption?", "English")
    ]
    
    print("Testing language detection...\n")
    
    for question, expected_language in test_cases:
        detected_language = "Vietnamese" if not _is_english_text(question) else "English"
        
        if detected_language == expected_language:
            status = "✅ CORRECT"
        else:
            status = "❌ INCORRECT"
        
        print(f"{status} - Expected: {expected_language}, Detected: {detected_language}")
        print(f"  Question: {question}")
        print()

def _is_english_text(text: str) -> bool:
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

async def main():
    """Main test function"""
    print("🚀 VIETNAMESE TRANSLATION TEST")
    print("Testing Vietnamese translation functionality")
    
    # Check if backend is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/health")
            if response.status_code != 200:
                print("❌ Backend is not running. Please start the backend first.")
                return
    except Exception as e:
        print("❌ Cannot connect to backend. Please start the backend first.")
        print(f"Error: {e}")
        return
    
    print("✅ Backend is running. Starting tests...\n")
    
    # Run tests
    passed, total = await test_vietnamese_translation()
    await test_streaming_vietnamese_translation()
    await test_language_detection()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Vietnamese translation tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All Vietnamese translation tests passed!")
        print("✅ Chatbot correctly translates English questions to Vietnamese.")
        print("✅ Chatbot maintains Vietnamese responses for Vietnamese questions.")
        print("✅ All responses are in Vietnamese.")
    else:
        print("⚠️ Some Vietnamese translation tests failed.")
        print("❌ Please check the translation implementation.")

if __name__ == "__main__":
    asyncio.run(main())
