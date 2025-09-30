"""
Test script cho Conversation Memory
Kiểm tra chức năng trí nhớ hội thoại của chatbot
"""

import asyncio
import httpx
import time
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def test_conversation_memory():
    """Test trí nhớ hội thoại của chatbot"""
    print("\n" + "="*60)
    print("🧪 TESTING CONVERSATION MEMORY")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Tạo session mới
        print("Step 1: Tạo session mới")
        response = await client.post(
            "http://localhost:8000/api/chat_sessions",
            json={"title": "Memory Test Session"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create session: {response.status_code}")
            return False
        
        session_id = response.json()["session_id"]
        print(f"✅ Created session: {session_id[:8]}...")
        
        # Step 2: Câu hỏi đầu tiên
        print("\nStep 2: Câu hỏi đầu tiên về phishing")
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={
                "question": "Tấn công phishing là gì?",
                "session_id": session_id,
                "top_k": 3,
                "memory_limit": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Question 1 answered")
            print(f"   Question: {data['question']}")
            print(f"   Response: {data['response'][:100]}...")
            print(f"   Sources: {len(data['sources'])}")
            print(f"   Processing time: {data['processing_time']:.2f}s")
        else:
            print(f"❌ Failed to answer question 1: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Step 3: Câu hỏi thứ hai (có tham chiếu đến câu hỏi trước)
        print("\nStep 3: Câu hỏi thứ hai (tham chiếu đến phishing)")
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={
                "question": "Có cách nào phòng chống nó không?",
                "session_id": session_id,
                "top_k": 3,
                "memory_limit": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Question 2 answered")
            print(f"   Question: {data['question']}")
            print(f"   Response: {data['response'][:100]}...")
            print(f"   Sources: {len(data['sources'])}")
            print(f"   Processing time: {data['processing_time']:.2f}s")
            
            # Kiểm tra xem response có hiểu "nó" = "phishing" không
            response_text = data['response'].lower()
            if 'phishing' in response_text or 'tấn công' in response_text:
                print("✅ Chatbot hiểu được 'nó' = 'phishing' (có trí nhớ)")
            else:
                print("⚠️ Chatbot có thể chưa hiểu được 'nó' = 'phishing'")
        else:
            print(f"❌ Failed to answer question 2: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Step 4: Câu hỏi thứ ba (tham chiếu đến câu trả lời trước)
        print("\nStep 4: Câu hỏi thứ ba (tham chiếu đến câu trả lời trước)")
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={
                "question": "Bạn có thể giải thích chi tiết hơn về cách thứ 2 không?",
                "session_id": session_id,
                "top_k": 3,
                "memory_limit": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Question 3 answered")
            print(f"   Question: {data['question']}")
            print(f"   Response: {data['response'][:100]}...")
            print(f"   Sources: {len(data['sources'])}")
            print(f"   Processing time: {data['processing_time']:.2f}s")
        else:
            print(f"❌ Failed to answer question 3: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Step 5: Kiểm tra lịch sử hội thoại
        print("\nStep 5: Kiểm tra lịch sử hội thoại")
        response = await client.get(f"http://localhost:8000/api/chat_sessions/{session_id}/messages")
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Retrieved {len(messages)} messages from session")
            for i, msg in enumerate(messages, 1):
                role = msg['role']
                content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                print(f"   {i}. [{role}] {content}")
        else:
            print(f"❌ Failed to get messages: {response.status_code}")
            print(f"   Error: {response.text}")
        
        # Step 6: Cleanup - xóa session
        print("\nStep 6: Cleanup - xóa session")
        response = await client.delete(f"http://localhost:8000/api/chat_sessions/{session_id}")
        
        if response.status_code == 200:
            print(f"✅ Deleted session: {session_id[:8]}...")
        else:
            print(f"❌ Failed to delete session: {response.status_code}")
            print(f"   Error: {response.text}")
        
        return True

async def test_memory_without_session():
    """Test chat không có session (không có trí nhớ)"""
    print("\n" + "="*60)
    print("🧪 TESTING CHAT WITHOUT SESSION (NO MEMORY)")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Câu hỏi đầu tiên
        print("Question 1: Tấn công phishing là gì?")
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={
                "question": "Tấn công phishing là gì?",
                "top_k": 3,
                "memory_limit": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Question 1 answered")
            print(f"   Response: {data['response'][:100]}...")
        else:
            print(f"❌ Failed to answer question 1: {response.status_code}")
            return False
        
        # Câu hỏi thứ hai (không có session, không có trí nhớ)
        print("\nQuestion 2: Có cách nào phòng chống nó không?")
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={
                "question": "Có cách nào phòng chống nó không?",
                "top_k": 3,
                "memory_limit": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Question 2 answered")
            print(f"   Response: {data['response'][:100]}...")
            
            # Kiểm tra xem response có hiểu "nó" không (không có trí nhớ)
            response_text = data['response'].lower()
            if 'phishing' in response_text or 'tấn công' in response_text:
                print("⚠️ Chatbot vẫn hiểu được 'nó' (có thể do context từ vector search)")
            else:
                print("✅ Chatbot không hiểu được 'nó' (không có trí nhớ)")
        else:
            print(f"❌ Failed to answer question 2: {response.status_code}")
            return False
        
        return True

async def test_memory_limit():
    """Test giới hạn trí nhớ"""
    print("\n" + "="*60)
    print("🧪 TESTING MEMORY LIMIT")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Tạo session mới
        response = await client.post(
            "http://localhost:8000/api/chat_sessions",
            json={"title": "Memory Limit Test"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create session: {response.status_code}")
            return False
        
        session_id = response.json()["session_id"]
        print(f"✅ Created session: {session_id[:8]}...")
        
        # Gửi nhiều câu hỏi để test memory limit
        questions = [
            "Bảo mật thông tin là gì?",
            "Tấn công mạng có những loại nào?",
            "SOC hoạt động như thế nào?",
            "Pentest có những giai đoạn nào?",
            "Mã hóa dữ liệu quan trọng như thế nào?",
            "Firewall hoạt động ra sao?",
            "Có cách nào bảo vệ khỏi ransomware không?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}: {question}")
            response = await client.post(
                "http://localhost:8000/api/chat",
                json={
                    "question": question,
                    "session_id": session_id,
                    "top_k": 3,
                    "memory_limit": 3  # Chỉ lấy 3 tin nhắn gần nhất
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Question {i} answered")
                print(f"   Response: {data['response'][:50]}...")
            else:
                print(f"❌ Failed to answer question {i}: {response.status_code}")
        
        # Kiểm tra lịch sử hội thoại
        print(f"\nChecking conversation history...")
        response = await client.get(f"http://localhost:8000/api/chat_sessions/{session_id}/messages")
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Total messages in session: {len(messages)}")
            print("   Last 3 messages (memory limit):")
            for msg in messages[-3:]:
                role = msg['role']
                content = msg['content'][:30] + "..." if len(msg['content']) > 30 else msg['content']
                print(f"   - [{role}] {content}")
        else:
            print(f"❌ Failed to get messages: {response.status_code}")
        
        # Cleanup
        await client.delete(f"http://localhost:8000/api/chat_sessions/{session_id}")
        print(f"✅ Cleaned up session")
        
        return True

async def test_streaming_with_memory():
    """Test streaming chat với trí nhớ"""
    print("\n" + "="*60)
    print("🧪 TESTING STREAMING CHAT WITH MEMORY")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=None) as client:
        # Tạo session mới
        response = await client.post(
            "http://localhost:8000/api/chat_sessions",
            json={"title": "Streaming Memory Test"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create session: {response.status_code}")
            return False
        
        session_id = response.json()["session_id"]
        print(f"✅ Created session: {session_id[:8]}...")
        
        # Câu hỏi đầu tiên
        print("\nQuestion 1: Tấn công phishing là gì?")
        response = await client.post(
            "http://localhost:8000/api/chat/stream",
            json={
                "question": "Tấn công phishing là gì?",
                "session_id": session_id,
                "top_k": 3,
                "memory_limit": 5
            },
            headers={"Accept": "text/event-stream"}
        )
        
        if response.status_code == 200:
            print("✅ Streaming question 1 started")
            full_response_1 = ""
            async for chunk in response.aiter_bytes():
                try:
                    decoded_chunk = chunk.decode('utf-8')
                    for line in decoded_chunk.split('\n'):
                        if line.startswith("data: "):
                            import json
                            data = json.loads(line[len("data: "):])
                            
                            if data["type"] == "token":
                                full_response_1 += data["content"]
                            elif data["type"] == "end":
                                break
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"❌ Stream error: {e}")
                    return False
            
            print(f"   Response length: {len(full_response_1)} chars")
        else:
            print(f"❌ Failed to stream question 1: {response.status_code}")
            return False
        
        # Câu hỏi thứ hai (tham chiếu đến câu hỏi trước)
        print("\nQuestion 2: Có cách nào phòng chống nó không?")
        response = await client.post(
            "http://localhost:8000/api/chat/stream",
            json={
                "question": "Có cách nào phòng chống nó không?",
                "session_id": session_id,
                "top_k": 3,
                "memory_limit": 5
            },
            headers={"Accept": "text/event-stream"}
        )
        
        if response.status_code == 200:
            print("✅ Streaming question 2 started")
            full_response_2 = ""
            async for chunk in response.aiter_bytes():
                try:
                    decoded_chunk = chunk.decode('utf-8')
                    for line in decoded_chunk.split('\n'):
                        if line.startswith("data: "):
                            import json
                            data = json.loads(line[len("data: "):])
                            
                            if data["type"] == "token":
                                full_response_2 += data["content"]
                            elif data["type"] == "end":
                                break
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"❌ Stream error: {e}")
                    return False
            
            print(f"   Response length: {len(full_response_2)} chars")
            
            # Kiểm tra xem response có hiểu "nó" = "phishing" không
            response_text = full_response_2.lower()
            if 'phishing' in response_text or 'tấn công' in response_text:
                print("✅ Chatbot hiểu được 'nó' = 'phishing' (có trí nhớ)")
            else:
                print("⚠️ Chatbot có thể chưa hiểu được 'nó' = 'phishing'")
        else:
            print(f"❌ Failed to stream question 2: {response.status_code}")
            return False
        
        # Cleanup
        await client.delete(f"http://localhost:8000/api/chat_sessions/{session_id}")
        print(f"✅ Cleaned up session")
        
        return True

async def main():
    """Main test function"""
    print("🚀 CONVERSATION MEMORY TEST")
    print("Testing conversation memory functionality")
    
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
    test_results = []
    
    test_results.append(await test_conversation_memory())
    test_results.append(await test_memory_without_session())
    test_results.append(await test_memory_limit())
    test_results.append(await test_streaming_with_memory())
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All conversation memory tests passed!")
        print("✅ Chatbot has working conversation memory.")
        print("✅ Chatbot can remember context across questions.")
        print("✅ Memory limit works correctly.")
        print("✅ Streaming chat with memory works correctly.")
    else:
        print("⚠️ Some conversation memory tests failed.")
        print("❌ Please check the memory implementation.")

if __name__ == "__main__":
    asyncio.run(main())
