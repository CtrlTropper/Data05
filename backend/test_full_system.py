"""
Test script cho toàn bộ hệ thống
Test tích hợp tất cả các module
"""

import asyncio
import requests
import json
import time
import os
from pathlib import Path

def test_system_integration():
    """Test tích hợp toàn bộ hệ thống"""
    
    print("🧪 Testing Full System Integration...")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api"
    
    # Test 1: Health Check
    print("\n1. 🏥 Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health: {health_data.get('status', 'unknown')}")
            print(f"   Version: {health_data.get('version', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: System Stats
    print("\n2. 📊 System Stats")
    try:
        # Chat stats
        chat_response = requests.get(f"{base_url}/chat/stats", timeout=10)
        if chat_response.status_code == 200:
            chat_stats = chat_response.json()
            print("✅ Chat System:")
            print(f"   LLM loaded: {chat_stats.get('llm_service', {}).get('model_loaded', False)}")
            print(f"   Embedding loaded: {chat_stats.get('embedding_service', {}).get('model_loaded', False)}")
            print(f"   FAISS vectors: {chat_stats.get('faiss_store', {}).get('total_vectors', 0)}")
        
        # Embedding stats
        embed_response = requests.get(f"{base_url}/embed/stats", timeout=10)
        if embed_response.status_code == 200:
            embed_stats = embed_response.json()
            print("✅ Embedding System:")
            print(f"   Model loaded: {embed_stats.get('embedding_service', {}).get('model_loaded', False)}")
            print(f"   FAISS vectors: {embed_stats.get('faiss_store', {}).get('total_vectors', 0)}")
        
        # Search stats
        search_response = requests.get(f"{base_url}/search/stats", timeout=10)
        if search_response.status_code == 200:
            search_stats = search_response.json()
            print("✅ Search System:")
            print(f"   Total vectors: {search_stats.get('faiss_store', {}).get('total_vectors', 0)}")
            
    except Exception as e:
        print(f"❌ Stats error: {e}")
    
    # Test 3: Document Management
    print("\n3. 📄 Document Management")
    try:
        # Get documents
        docs_response = requests.get(f"{base_url}/documents", timeout=10)
        if docs_response.status_code == 200:
            docs_data = docs_response.json()
            print(f"✅ Documents: {docs_data.get('total', 0)} total")
            
            # Test document operations if documents exist
            if docs_data.get('documents'):
                doc_id = docs_data['documents'][0]['id']
                print(f"   Testing with document: {doc_id}")
                
                # Get document details
                doc_response = requests.get(f"{base_url}/documents/{doc_id}", timeout=10)
                if doc_response.status_code == 200:
                    doc_data = doc_response.json()
                    print(f"   Document: {doc_data.get('filename', 'unknown')}")
                    print(f"   Size: {doc_data.get('size', 0)} bytes")
                    print(f"   Selected: {doc_data.get('selected', False)}")
        else:
            print(f"❌ Documents error: {docs_response.status_code}")
            
    except Exception as e:
        print(f"❌ Document management error: {e}")
    
    # Test 4: Embedding System
    print("\n4. 🔤 Embedding System")
    try:
        # Test text embedding
        embed_request = {
            "text": "Đây là đoạn văn bản test cho hệ thống embedding"
        }
        
        embed_response = requests.post(
            f"{base_url}/embed/text",
            json=embed_request,
            timeout=30
        )
        
        if embed_response.status_code == 200:
            embed_data = embed_response.json()
            print("✅ Text Embedding:")
            print(f"   Text length: {embed_data.get('text_length', 0)}")
            print(f"   Embedding dimension: {embed_data.get('dimension', 0)}")
            print(f"   Embedding preview: {embed_data.get('embedding', [])[:3]}...")
        else:
            print(f"❌ Embedding error: {embed_response.status_code}")
            
    except Exception as e:
        print(f"❌ Embedding system error: {e}")
    
    # Test 5: Search System
    print("\n5. 🔍 Search System")
    try:
        # Test text search
        search_request = {
            "query": "trí tuệ nhân tạo và machine learning",
            "top_k": 3
        }
        
        search_response = requests.post(
            f"{base_url}/search/text",
            json=search_request,
            timeout=30
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            print("✅ Text Search:")
            print(f"   Query: {search_data.get('query', '')}")
            print(f"   Results: {search_data.get('total_found', 0)}")
            print(f"   Search time: {search_data.get('search_time', 0):.3f}s")
            
            # Show first result
            results = search_data.get('results', [])
            if results:
                first_result = results[0]
                print(f"   Best match: {first_result.get('content', '')[:100]}...")
                print(f"   Similarity: {first_result.get('similarity_score', 0):.3f}")
        else:
            print(f"❌ Search error: {search_response.status_code}")
            
    except Exception as e:
        print(f"❌ Search system error: {e}")
    
    # Test 6: Chat System
    print("\n6. 💬 Chat System")
    try:
        # Test basic chat
        chat_request = {
            "question": "Xin chào! Bạn có thể giới thiệu về bản thân không?",
            "top_k": 3
        }
        
        chat_response = requests.post(
            f"{base_url}/chat",
            json=chat_request,
            timeout=60
        )
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            print("✅ Basic Chat:")
            print(f"   Question: {chat_data.get('question', '')}")
            print(f"   Response: {chat_data.get('response', '')[:150]}...")
            print(f"   Processing time: {chat_data.get('processing_time', 0):.3f}s")
            print(f"   Sources used: {len(chat_data.get('sources', []))}")
        else:
            print(f"❌ Chat error: {chat_response.status_code}")
            print(f"   Error: {chat_response.text}")
            
    except Exception as e:
        print(f"❌ Chat system error: {e}")
    
    # Test 7: Document Chat (if documents exist)
    print("\n7. 📄 Document Chat")
    try:
        # Get documents first
        docs_response = requests.get(f"{base_url}/documents", timeout=10)
        if docs_response.status_code == 200:
            docs_data = docs_response.json()
            
            if docs_data.get('documents'):
                doc_id = docs_data['documents'][0]['id']
                
                # Test document chat
                doc_chat_request = {
                    "question": "Hãy tóm tắt nội dung chính của tài liệu này",
                    "top_k": 3
                }
                
                doc_chat_response = requests.post(
                    f"{base_url}/chat/document/{doc_id}",
                    json=doc_chat_request,
                    timeout=60
                )
                
                if doc_chat_response.status_code == 200:
                    doc_chat_data = doc_chat_response.json()
                    print("✅ Document Chat:")
                    print(f"   Question: {doc_chat_data.get('question', '')}")
                    print(f"   Response: {doc_chat_data.get('response', '')[:150]}...")
                    print(f"   Document ID: {doc_chat_data.get('doc_id', '')}")
                    print(f"   Sources: {len(doc_chat_data.get('sources', []))}")
                else:
                    print(f"❌ Document chat error: {doc_chat_response.status_code}")
            else:
                print("⚠️  No documents available for document chat test")
        else:
            print(f"❌ Failed to get documents: {docs_response.status_code}")
            
    except Exception as e:
        print(f"❌ Document chat error: {e}")
    
    # Test 8: Performance Test
    print("\n8. ⚡ Performance Test")
    try:
        questions = [
            "Trí tuệ nhân tạo là gì?",
            "Machine learning hoạt động như thế nào?",
            "Deep learning có những ứng dụng gì?"
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
                timeout=60
            )
            end_time = time.time()
            
            if response.status_code == 200:
                successful_requests += 1
                request_time = end_time - start_time
                total_time += request_time
                print(f"   Question {i}: {request_time:.3f}s")
            else:
                print(f"   Question {i}: Failed ({response.status_code})")
        
        if successful_requests > 0:
            avg_time = total_time / successful_requests
            print(f"✅ Performance Test:")
            print(f"   Successful: {successful_requests}/{len(questions)}")
            print(f"   Average time: {avg_time:.3f}s")
        else:
            print("❌ No successful requests in performance test")
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Full System Integration Test Completed!")
    print("=" * 60)

def main():
    """Main test function"""
    print("🚀 Starting Full System Integration Test...")
    print("Make sure the server is running: python start.py")
    print("Waiting 5 seconds for server to be ready...")
    time.sleep(5)
    
    test_system_integration()

if __name__ == "__main__":
    main()
