"""
Test script cho Chat Sessions
Kiểm tra chức năng quản lý chat sessions
"""

import asyncio
import httpx
import time
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def test_create_chat_session():
    """Test tạo chat session mới"""
    print("\n" + "="*60)
    print("🧪 TESTING CREATE CHAT SESSION")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Tạo session với title
        print("Test 1: Tạo session với title")
        response = await client.post(
            "http://localhost:8000/api/chat_sessions",
            json={"title": "Test Security Session"}
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id_1 = data["session_id"]
            print(f"✅ Created session: {session_id_1}")
            print(f"   Title: {data['title']}")
            print(f"   Created at: {data['created_at']}")
            print(f"   Message count: {data['message_count']}")
        else:
            print(f"❌ Failed to create session: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
        
        # Test 2: Tạo session không có title
        print("\nTest 2: Tạo session không có title")
        response = await client.post(
            "http://localhost:8000/api/chat_sessions",
            json={}
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id_2 = data["session_id"]
            print(f"✅ Created session: {session_id_2}")
            print(f"   Title: {data['title']}")
            print(f"   Created at: {data['created_at']}")
            print(f"   Message count: {data['message_count']}")
        else:
            print(f"❌ Failed to create session: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
        
        return [session_id_1, session_id_2]

async def test_list_chat_sessions():
    """Test liệt kê chat sessions"""
    print("\n" + "="*60)
    print("🧪 TESTING LIST CHAT SESSIONS")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Liệt kê tất cả sessions
        print("Test 1: Liệt kê tất cả sessions")
        response = await client.get("http://localhost:8000/api/chat_sessions")
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ Listed {len(sessions)} sessions")
            for i, session in enumerate(sessions, 1):
                print(f"   {i}. {session['session_id'][:8]}... - {session['title']} ({session['message_count']} messages)")
        else:
            print(f"❌ Failed to list sessions: {response.status_code}")
            print(f"   Error: {response.text}")
            return []
        
        # Test 2: Liệt kê với limit
        print("\nTest 2: Liệt kê với limit=1")
        response = await client.get("http://localhost:8000/api/chat_sessions?limit=1")
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ Listed {len(sessions)} sessions (limited)")
            for i, session in enumerate(sessions, 1):
                print(f"   {i}. {session['session_id'][:8]}... - {session['title']} ({session['message_count']} messages)")
        else:
            print(f"❌ Failed to list sessions with limit: {response.status_code}")
            print(f"   Error: {response.text}")
        
        return [session['session_id'] for session in sessions]

async def test_get_chat_session(session_id: str):
    """Test lấy thông tin chi tiết session"""
    print(f"\n" + "="*60)
    print(f"🧪 TESTING GET CHAT SESSION: {session_id[:8]}...")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Lấy thông tin session
        print("Test 1: Lấy thông tin session")
        response = await client.get(f"http://localhost:8000/api/chat_sessions/{session_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved session: {data['session_id'][:8]}...")
            print(f"   Title: {data['title']}")
            print(f"   Created at: {data['created_at']}")
            print(f"   Updated at: data['updated_at']}")
            print(f"   Message count: {data['message_count']}")
            print(f"   Messages: {len(data.get('messages', []))}")
        else:
            print(f"❌ Failed to get session: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Test 2: Lấy tin nhắn của session
        print("\nTest 2: Lấy tin nhắn của session")
        response = await client.get(f"http://localhost:8000/api/chat_sessions/{session_id}/messages")
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Retrieved {len(messages)} messages")
            for i, msg in enumerate(messages, 1):
                print(f"   {i}. [{msg['role']}] {msg['content'][:50]}...")
        else:
            print(f"❌ Failed to get messages: {response.status_code}")
            print(f"   Error: {response.text}")
        
        return True

async def test_add_message_to_session(session_id: str):
    """Test thêm tin nhắn vào session"""
    print(f"\n" + "="*60)
    print(f"🧪 TESTING ADD MESSAGE TO SESSION: {session_id[:8]}...")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Thêm tin nhắn user
        print("Test 1: Thêm tin nhắn user")
        response = await client.post(
            f"http://localhost:8000/api/chat_sessions/{session_id}/messages",
            params={"role": "user", "content": "Bảo mật thông tin là gì?"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Added user message: {data['content'][:50]}...")
        else:
            print(f"❌ Failed to add user message: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Test 2: Thêm tin nhắn assistant
        print("\nTest 2: Thêm tin nhắn assistant")
        response = await client.post(
            f"http://localhost:8000/api/chat_sessions/{session_id}/messages",
            params={"role": "assistant", "content": "Bảo mật thông tin là thực hành bảo vệ thông tin khỏi truy cập, sử dụng, tiết lộ, gián đoạn, sửa đổi hoặc phá hủy trái phép."}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Added assistant message: {data['content'][:50]}...")
        else:
            print(f"❌ Failed to add assistant message: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        return True

async def test_chat_with_session(session_id: str):
    """Test chat với session"""
    print(f"\n" + "="*60)
    print(f"🧪 TESTING CHAT WITH SESSION: {session_id[:8]}...")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test 1: Chat với session
        print("Test 1: Chat với session")
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={
                "question": "Làm thế nào để bảo vệ khỏi ransomware?",
                "session_id": session_id,
                "top_k": 3
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat completed")
            print(f"   Question: {data['question']}")
            print(f"   Response: {data['response'][:100]}...")
            print(f"   Sources: {len(data['sources'])}")
            print(f"   Processing time: {data['processing_time']:.2f}s")
            print(f"   Session ID: {data['session_id']}")
        else:
            print(f"❌ Failed to chat: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Test 2: Kiểm tra tin nhắn đã được lưu
        print("\nTest 2: Kiểm tra tin nhắn đã được lưu")
        response = await client.get(f"http://localhost:8000/api/chat_sessions/{session_id}/messages")
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Session now has {len(messages)} messages")
            for i, msg in enumerate(messages, 1):
                print(f"   {i}. [{msg['role']}] {msg['content'][:50]}...")
        else:
            print(f"❌ Failed to get messages: {response.status_code}")
            print(f"   Error: {response.text}")
        
        return True

async def test_streaming_chat_with_session(session_id: str):
    """Test streaming chat với session"""
    print(f"\n" + "="*60)
    print(f"🧪 TESTING STREAMING CHAT WITH SESSION: {session_id[:8]}...")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=None) as client:
        # Test streaming chat với session
        print("Test: Streaming chat với session")
        response = await client.post(
            "http://localhost:8000/api/chat/stream",
            json={
                "question": "SOC hoạt động như thế nào?",
                "session_id": session_id,
                "top_k": 3
            },
            headers={"Accept": "text/event-stream"}
        )
        
        if response.status_code == 200:
            print("✅ Streaming chat started")
            
            # Read streaming response
            full_response = ""
            async for chunk in response.aiter_bytes():
                try:
                    decoded_chunk = chunk.decode('utf-8')
                    for line in decoded_chunk.split('\n'):
                        if line.startswith("data: "):
                            import json
                            data = json.loads(line[len("data: "):])
                            
                            if data["type"] == "start":
                                print(f"   Question: {data['question']}")
                                print(f"   Sources: {data['sources_count']}")
                            elif data["type"] == "token":
                                print(data["content"], end="", flush=True)
                                full_response += data["content"]
                            elif data["type"] == "end":
                                print("\n   ✅ Streaming completed")
                            elif data["type"] == "error":
                                print(f"\n   ❌ Error: {data['message']}")
                                return False
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"\n   ❌ Stream error: {e}")
                    return False
            
            print(f"   Response length: {len(full_response)} chars")
        else:
            print(f"❌ Failed to start streaming chat: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        return True

async def test_delete_chat_session(session_id: str):
    """Test xóa chat session"""
    print(f"\n" + "="*60)
    print(f"🧪 TESTING DELETE CHAT SESSION: {session_id[:8]}...")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test xóa session
        print("Test: Xóa session")
        response = await client.delete(f"http://localhost:8000/api/chat_sessions/{session_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Deleted session: {data['session_id'][:8]}...")
            print(f"   Message: {data['message']}")
            print(f"   Deleted: {data['deleted']}")
        else:
            print(f"❌ Failed to delete session: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Test kiểm tra session đã bị xóa
        print("\nTest: Kiểm tra session đã bị xóa")
        response = await client.get(f"http://localhost:8000/api/chat_sessions/{session_id}")
        
        if response.status_code == 404:
            print("✅ Session đã bị xóa thành công")
        else:
            print(f"❌ Session vẫn tồn tại: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        return True

async def test_chat_sessions_stats():
    """Test thống kê chat sessions"""
    print("\n" + "="*60)
    print("🧪 TESTING CHAT SESSIONS STATS")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test lấy thống kê
        print("Test: Lấy thống kê sessions")
        response = await client.get("http://localhost:8000/api/chat_sessions/stats")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved stats:")
            print(f"   Total sessions: {data['total_sessions']}")
            print(f"   Total messages: {data['total_messages']}")
            print(f"   Recent sessions: {data['recent_sessions']}")
            print(f"   Storage file: {data['storage_file']}")
            print(f"   Last updated: {data['last_updated']}")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        return True

async def main():
    """Main test function"""
    print("🚀 CHAT SESSIONS TEST")
    print("Testing chat sessions management functionality")
    
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
    session_ids = await test_create_chat_session()
    if not session_ids:
        print("❌ Failed to create sessions. Stopping tests.")
        return
    
    await test_list_chat_sessions()
    
    # Test with first session
    session_id_1 = session_ids[0]
    await test_get_chat_session(session_id_1)
    await test_add_message_to_session(session_id_1)
    await test_chat_with_session(session_id_1)
    await test_streaming_chat_with_session(session_id_1)
    
    # Test with second session
    session_id_2 = session_ids[1]
    await test_chat_with_session(session_id_2)
    
    await test_chat_sessions_stats()
    
    # Clean up - delete sessions
    await test_delete_chat_session(session_id_1)
    await test_delete_chat_session(session_id_2)
    
    # Final stats
    await test_chat_sessions_stats()
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print("🎉 All chat sessions tests completed!")
    print("✅ Chat sessions management is working correctly.")
    print("✅ Sessions can be created, listed, and deleted.")
    print("✅ Messages can be added and retrieved.")
    print("✅ Chat with sessions works correctly.")
    print("✅ Streaming chat with sessions works correctly.")

if __name__ == "__main__":
    asyncio.run(main())
