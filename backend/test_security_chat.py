"""
Test script cho Security Chat
Kiểm tra chatbot chỉ trả lời câu hỏi về ATTT
"""

import asyncio
import httpx
import time
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def test_security_chat():
    """Test security-focused chat functionality"""
    print("\n" + "="*60)
    print("🧪 TESTING SECURITY CHAT")
    print("="*60)
    
    # Test cases
    test_cases = [
        # Security-related questions (should be processed)
        {
            "question": "Bảo mật thông tin là gì?",
            "should_process": True,
            "category": "Basic Security"
        },
        {
            "question": "Làm thế nào để bảo vệ khỏi ransomware?",
            "should_process": True,
            "category": "Malware Protection"
        },
        {
            "question": "SOC hoạt động như thế nào?",
            "should_process": True,
            "category": "Security Operations"
        },
        {
            "question": "Pentest có những giai đoạn nào?",
            "should_process": True,
            "category": "Penetration Testing"
        },
        {
            "question": "Mã hóa dữ liệu quan trọng như thế nào?",
            "should_process": True,
            "category": "Cryptography"
        },
        
        # Non-security questions (should be rejected)
        {
            "question": "Thời tiết hôm nay như thế nào?",
            "should_process": False,
            "category": "Weather"
        },
        {
            "question": "Cách nấu phở bò?",
            "should_process": False,
            "category": "Cooking"
        },
        {
            "question": "Bóng đá World Cup 2022 diễn ra ở đâu?",
            "should_process": False,
            "category": "Sports"
        },
        {
            "question": "Du lịch Đà Nẵng có gì hay?",
            "should_process": False,
            "category": "Travel"
        },
        {
            "question": "Giá vàng hôm nay bao nhiêu?",
            "should_process": False,
            "category": "Finance"
        }
    ]
    
    # Test chat endpoint
    print("Testing /api/chat endpoint...\n")
    
    passed = 0
    total = len(test_cases)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, test_case in enumerate(test_cases, 1):
            question = test_case["question"]
            should_process = test_case["should_process"]
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
                    
                    # Check if response is rejection message
                    is_rejection = "Xin lỗi, tôi chỉ hỗ trợ các câu hỏi liên quan đến An ninh An toàn thông tin" in response_text
                    
                    # Determine if test passed
                    if should_process and not is_rejection:
                        status = "✅ PASS"
                        passed += 1
                    elif not should_process and is_rejection:
                        status = "✅ PASS"
                        passed += 1
                    else:
                        status = "❌ FAIL"
                    
                    print(f"Test {i:2d}: {status}")
                    print(f"  Question: {question}")
                    print(f"  Category: {category}")
                    print(f"  Should process: {should_process}")
                    print(f"  Is rejection: {is_rejection}")
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

async def test_streaming_security_chat():
    """Test streaming security chat"""
    print("\n" + "="*60)
    print("🧪 TESTING STREAMING SECURITY CHAT")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "question": "Bảo mật mạng là gì?",
            "should_process": True,
            "category": "Network Security"
        },
        {
            "question": "Cách nấu cơm?",
            "should_process": False,
            "category": "Cooking"
        }
    ]
    
    print("Testing /api/chat/stream endpoint...\n")
    
    async with httpx.AsyncClient(timeout=None) as client:
        for i, test_case in enumerate(test_cases, 1):
            question = test_case["question"]
            should_process = test_case["should_process"]
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
                    print(f"  Should process: {should_process}")
                    
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
                    
                    # Check result
                    if should_process and not rejection_detected:
                        status = "✅ PASS"
                    elif not should_process and rejection_detected:
                        status = "✅ PASS"
                    else:
                        status = "❌ FAIL"
                    
                    print(f"  Status: {status}")
                    print(f"  Rejection detected: {rejection_detected}")
                    print(f"  Response length: {len(full_response)} chars")
                    print()
                    
                else:
                    print(f"Test {i}: ❌ FAIL - HTTP {response.status_code}")
                    print(f"  Question: {question}")
                    print()
                    
            except Exception as e:
                print(f"Test {i}: ❌ ERROR - {e}")
                print(f"  Question: {question}")
                print()

async def test_chat_stats():
    """Test chat stats with security filter info"""
    print("\n" + "="*60)
    print("🧪 TESTING CHAT STATS")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/chat/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                print("Chat System Statistics:")
                print(f"  LLM Service: {data.get('llm_service', {}).get('loaded', False)}")
                print(f"  Embedding Service: {data.get('embedding_service', {}).get('loaded', False)}")
                print(f"  FAISS Store: {data.get('faiss_store', {}).get('total_vectors', 0)} vectors")
                
                # Security filter info
                security_filter = data.get('security_filter', {})
                print(f"  Security Filter:")
                print(f"    Total keywords: {security_filter.get('total_security_keywords', 0)}")
                print(f"    Total phrases: {security_filter.get('total_security_phrases', 0)}")
                print(f"    Security domains: {len(security_filter.get('security_domains', []))}")
                
                # Chat capabilities
                capabilities = data.get('chat_capabilities', {})
                print(f"  Chat Capabilities:")
                print(f"    Security filtered: {capabilities.get('security_filtered', False)}")
                print(f"    RAG enabled: {capabilities.get('rag_enabled', False)}")
                print(f"    Streaming chat: {capabilities.get('streaming_chat', False)}")
                
                print("✅ Chat stats retrieved successfully")
                return True
                
            else:
                print(f"❌ Failed to get chat stats: HTTP {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error getting chat stats: {e}")
        return False

async def test_security_domain_classification():
    """Test security domain classification"""
    print("\n" + "="*60)
    print("🧪 TESTING SECURITY DOMAIN CLASSIFICATION")
    print("="*60)
    
    # Test different security domains
    domain_tests = [
        ("Network Security", "Firewall hoạt động như thế nào?"),
        ("Application Security", "OWASP Top 10 là gì?"),
        ("Data Protection", "Mã hóa AES hoạt động ra sao?"),
        ("Identity Management", "Single Sign-On là gì?"),
        ("Incident Response", "Xử lý sự cố bảo mật như thế nào?"),
        ("Risk Management", "Đánh giá rủi ro bảo mật?"),
        ("Compliance", "PCI DSS có những yêu cầu gì?"),
        ("Security Operations", "SIEM hoạt động như thế nào?"),
        ("Penetration Testing", "Kiểm thử xâm nhập có những giai đoạn nào?"),
        ("Security Awareness", "Đào tạo nhận thức bảo mật quan trọng như thế nào?")
    ]
    
    print("Testing security domain classification...\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for expected_domain, question in domain_tests:
            try:
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
                    
                    # Check if it's a security-related response (not rejection)
                    is_security_response = "Xin lỗi, tôi chỉ hỗ trợ" not in response_text
                    
                    if is_security_response:
                        print(f"✅ {expected_domain}: Question processed")
                        print(f"  Question: {question}")
                        print(f"  Response: {response_text[:100]}...")
                    else:
                        print(f"❌ {expected_domain}: Question rejected")
                        print(f"  Question: {question}")
                    print()
                    
                else:
                    print(f"❌ {expected_domain}: HTTP {response.status_code}")
                    print(f"  Question: {question}")
                    print()
                    
            except Exception as e:
                print(f"❌ {expected_domain}: Error - {e}")
                print(f"  Question: {question}")
                print()

async def main():
    """Main test function"""
    print("🚀 SECURITY CHAT TEST")
    print("Testing security-focused chatbot functionality")
    
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
    passed, total = await test_security_chat()
    await test_streaming_security_chat()
    await test_chat_stats()
    await test_security_domain_classification()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Security chat tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All security chat tests passed!")
        print("✅ Chatbot correctly filters non-security questions.")
        print("✅ Chatbot processes security-related questions.")
    else:
        print("⚠️ Some security chat tests failed.")
        print("❌ Please check the security filter implementation.")

if __name__ == "__main__":
    asyncio.run(main())
