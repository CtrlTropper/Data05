"""
Test script cho chatbot functionality
"""

import asyncio
import requests
import json
import time

async def test_chatbot_functionality():
    """Test các chức năng chatbot"""
    
    print("🧪 Testing Chatbot Functionality...")
    
    base_url = "http://localhost:8000/api"
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Chat stats
    print("\n2. Testing chat stats...")
    try:
        response = requests.get(f"{base_url}/chat/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Chat stats retrieved:")
            print(f"   LLM loaded: {stats.get('llm_service', {}).get('model_loaded', False)}")
            print(f"   Embedding loaded: {stats.get('embedding_service', {}).get('model_loaded', False)}")
            print(f"   FAISS vectors: {stats.get('faiss_store', {}).get('total_vectors', 0)}")
        else:
            print(f"❌ Chat stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat stats error: {e}")
    
    # Test 3: Basic chat (without context)
    print("\n3. Testing basic chat...")
    try:
        chat_request = {
            "question": "Xin chào! Bạn có thể giới thiệu về bản thân không?",
            "top_k": 3
        }
        
        response = requests.post(
            f"{base_url}/chat",
            json=chat_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Basic chat successful:")
            print(f"   Question: {result.get('question', '')}")
            print(f"   Response: {result.get('response', '')[:100]}...")
            print(f"   Processing time: {result.get('processing_time', 0):.3f}s")
            print(f"   Sources: {len(result.get('sources', []))}")
        else:
            print(f"❌ Basic chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Basic chat error: {e}")
    
    # Test 4: Chat with document filter
    print("\n4. Testing chat with document filter...")
    try:
        # First, get documents
        docs_response = requests.get(f"{base_url}/documents")
        if docs_response.status_code == 200:
            docs = docs_response.json()
            if docs.get('documents'):
                doc_id = docs['documents'][0]['id']
                
                chat_request = {
                    "question": "Hãy tóm tắt nội dung chính của tài liệu này",
                    "doc_id": doc_id,
                    "top_k": 3
                }
                
                response = requests.post(
                    f"{base_url}/chat",
                    json=chat_request,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Document chat successful:")
                    print(f"   Question: {result.get('question', '')}")
                    print(f"   Response: {result.get('response', '')[:100]}...")
                    print(f"   Sources: {len(result.get('sources', []))}")
                    print(f"   Document ID: {result.get('doc_id', '')}")
                else:
                    print(f"❌ Document chat failed: {response.status_code}")
            else:
                print("⚠️ No documents available for testing")
        else:
            print(f"❌ Failed to get documents: {docs_response.status_code}")
    except Exception as e:
        print(f"❌ Document chat error: {e}")
    
    # Test 5: Search functionality
    print("\n5. Testing search functionality...")
    try:
        search_request = {
            "query": "trí tuệ nhân tạo",
            "top_k": 3
        }
        
        response = requests.post(
            f"{base_url}/search/text",
            json=search_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search successful:")
            print(f"   Query: {result.get('query', '')}")
            print(f"   Results: {result.get('total_found', 0)}")
            print(f"   Search time: {result.get('search_time', 0):.3f}s")
        else:
            print(f"❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    # Test 6: Embedding functionality
    print("\n6. Testing embedding functionality...")
    try:
        embed_request = {
            "text": "Đây là đoạn văn bản test cho embedding"
        }
        
        response = requests.post(
            f"{base_url}/embed/text",
            json=embed_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Embedding successful:")
            print(f"   Text length: {result.get('text_length', 0)}")
            print(f"   Embedding dimension: {result.get('dimension', 0)}")
            print(f"   Embedding preview: {result.get('embedding', [])[:5]}...")
        else:
            print(f"❌ Embedding failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Embedding error: {e}")
    
    # Test 7: Performance test
    print("\n7. Testing performance...")
    try:
        questions = [
            "Trí tuệ nhân tạo là gì?",
            "Machine learning hoạt động như thế nào?",
            "Deep learning có những ứng dụng gì?",
            "Natural language processing là gì?",
            "Computer vision được sử dụng ở đâu?"
        ]
        
        total_time = 0
        successful_requests = 0
        
        for i, question in enumerate(questions, 1):
            chat_request = {
                "question": question,
                "top_k": 3
            }
            
            start_time = time.time()
            response = requests.post(
                f"{base_url}/chat",
                json=chat_request,
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                successful_requests += 1
                total_time += (end_time - start_time)
                print(f"   Question {i}: {end_time - start_time:.3f}s")
            else:
                print(f"   Question {i}: Failed ({response.status_code})")
        
        if successful_requests > 0:
            avg_time = total_time / successful_requests
            print(f"✅ Performance test completed:")
            print(f"   Successful requests: {successful_requests}/{len(questions)}")
            print(f"   Average response time: {avg_time:.3f}s")
        else:
            print("❌ No successful requests in performance test")
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
    
    print("\n✅ Chatbot testing completed!")

if __name__ == "__main__":
    asyncio.run(test_chatbot_functionality())
