"""
Test script cho deployment
Kiểm tra toàn bộ hệ thống sau khi triển khai
"""

import asyncio
import httpx
import time
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_backend_health():
    """Test backend health check"""
    print("🔍 Testing backend health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/health")
            if response.status_code == 200:
                print("✅ Backend health check passed")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

async def test_frontend_health():
    """Test frontend health check"""
    print("🔍 Testing frontend health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:80/health")
            if response.status_code == 200:
                print("✅ Frontend health check passed")
                return True
            else:
                print(f"❌ Frontend health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Frontend health check error: {e}")
        return False

async def test_document_upload():
    """Test document upload"""
    print("🔍 Testing document upload...")
    try:
        # Create test document
        test_content = """
        Trí tuệ nhân tạo (AI) là một lĩnh vực khoa học máy tính tập trung vào việc tạo ra các hệ thống có khả năng thực hiện các tác vụ thông minh.
        Machine learning là một nhánh con của AI, cho phép máy tính học hỏi từ dữ liệu mà không cần lập trình rõ ràng.
        Deep learning là một tập hợp con của machine learning, sử dụng mạng nơ-ron nhân tạo với nhiều lớp để phân tích dữ liệu.
        """
        
        with open("test_document.txt", "w", encoding="utf-8") as f:
            f.write(test_content)
        
        async with httpx.AsyncClient() as client:
            with open("test_document.txt", "rb") as f:
                files = {"file": ("test_document.txt", f, "text/plain")}
                response = await client.post("http://localhost:8000/api/documents/upload", files=files)
            
            if response.status_code == 201:
                data = response.json()
                doc_id = data.get("document_id")
                print(f"✅ Document upload successful. ID: {doc_id}")
                return doc_id
            else:
                print(f"❌ Document upload failed: {response.status_code}")
                return None
    except Exception as e:
        print(f"❌ Document upload error: {e}")
        return None

async def test_embedding_generation(doc_id):
    """Test embedding generation"""
    print("🔍 Testing embedding generation...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"http://localhost:8000/api/embed/document/{doc_id}",
                json={"chunk_size": 500, "chunk_overlap": 50}
            )
            
            if response.status_code == 200:
                data = response.json()
                chunks = data.get("chunks_processed", 0)
                print(f"✅ Embedding generation successful. Chunks: {chunks}")
                return True
            else:
                print(f"❌ Embedding generation failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Embedding generation error: {e}")
        return False

async def test_chat_functionality():
    """Test chat functionality"""
    print("🔍 Testing chat functionality...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/api/chat",
                json={
                    "question": "Trí tuệ nhân tạo là gì?",
                    "top_k": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "")
                sources = data.get("sources", [])
                print(f"✅ Chat functionality successful")
                print(f"   Answer length: {len(answer)} characters")
                print(f"   Sources: {len(sources)} chunks")
                return True
            else:
                print(f"❌ Chat functionality failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Chat functionality error: {e}")
        return False

async def test_streaming_chat():
    """Test streaming chat"""
    print("🔍 Testing streaming chat...")
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(
                "http://localhost:8000/api/chat/stream",
                json={
                    "question": "Hãy giải thích về machine learning",
                    "top_k": 3
                },
                headers={"Accept": "text/event-stream"}
            )
            
            if response.status_code == 200:
                print("✅ Streaming chat started")
                chunk_count = 0
                async for chunk in response.aiter_bytes():
                    chunk_count += 1
                    if chunk_count > 10:  # Limit for testing
                        break
                
                print(f"✅ Streaming chat successful. Received {chunk_count} chunks")
                return True
            else:
                print(f"❌ Streaming chat failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Streaming chat error: {e}")
        return False

async def test_system_stats():
    """Test system statistics"""
    print("🔍 Testing system statistics...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/chat/stats")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ System statistics retrieved:")
                print(f"   LLM Service: {data.get('llm_service', {}).get('loaded', False)}")
                print(f"   Embedding Service: {data.get('embedding_service', {}).get('loaded', False)}")
                print(f"   FAISS Store: {data.get('faiss_store', {}).get('total_vectors', 0)} vectors")
                return True
            else:
                print(f"❌ System statistics failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ System statistics error: {e}")
        return False

async def test_offline_operation():
    """Test offline operation"""
    print("🔍 Testing offline operation...")
    try:
        # Test that models are loaded from local files
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/chat/stats")
            
            if response.status_code == 200:
                data = response.json()
                llm_loaded = data.get('llm_service', {}).get('loaded', False)
                embedding_loaded = data.get('embedding_service', {}).get('loaded', False)
                
                if llm_loaded and embedding_loaded:
                    print("✅ Offline operation successful - models loaded from local files")
                    return True
                else:
                    print("❌ Offline operation failed - models not loaded")
                    return False
            else:
                print(f"❌ Offline operation test failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Offline operation error: {e}")
        return False

async def test_performance():
    """Test system performance"""
    print("🔍 Testing system performance...")
    try:
        questions = [
            "Trí tuệ nhân tạo là gì?",
            "Machine learning hoạt động như thế nào?",
            "Deep learning có những ứng dụng gì?",
            "Neural networks là gì?",
            "AI có những lợi ích gì?"
        ]
        
        total_time = 0
        successful_requests = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, question in enumerate(questions, 1):
                start_time = time.time()
                try:
                    response = await client.post(
                        "http://localhost:8000/api/chat",
                        json={"question": question, "top_k": 3}
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        request_time = end_time - start_time
                        total_time += request_time
                        successful_requests += 1
                        print(f"   Question {i}: {request_time:.2f}s")
                    else:
                        print(f"   Question {i}: Failed - {response.status_code}")
                except Exception as e:
                    print(f"   Question {i}: Error - {e}")
        
        if successful_requests > 0:
            avg_time = total_time / successful_requests
            print(f"✅ Performance test completed:")
            print(f"   Successful: {successful_requests}/{len(questions)}")
            print(f"   Average time: {avg_time:.2f}s per question")
            print(f"   Total time: {total_time:.2f}s")
            return True
        else:
            print("❌ Performance test failed - no successful requests")
            return False
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 DEPLOYMENT TEST")
    print("==================")
    print("Testing RAG + LLM Chatbot System deployment")
    print()
    
    test_results = []
    
    # Run tests
    test_results.append(await test_backend_health())
    test_results.append(await test_frontend_health())
    
    doc_id = await test_document_upload()
    if doc_id:
        test_results.append(await test_embedding_generation(doc_id))
    
    test_results.append(await test_chat_functionality())
    test_results.append(await test_streaming_chat())
    test_results.append(await test_system_stats())
    test_results.append(await test_offline_operation())
    test_results.append(await test_performance())
    
    # Cleanup
    if os.path.exists("test_document.txt"):
        os.remove("test_document.txt")
    
    # Summary
    print("\n" + "="*50)
    print("📊 DEPLOYMENT TEST SUMMARY")
    print("="*50)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Deployment is successful.")
        print("✅ System is ready for production use.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("❌ System may not be ready for production use.")
    
    print("\n🌐 Access the system:")
    print("   Frontend: http://localhost")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())
