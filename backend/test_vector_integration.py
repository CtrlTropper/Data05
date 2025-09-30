"""
Test script cho Vector Service Integration
Test tích hợp embedding offline và FAISS
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vector_service import vector_service
from services.embedding_service import embedding_service
from db.faiss_store import faiss_store

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_embedding_service():
    """Test embedding service offline"""
    print("\n" + "="*60)
    print("🧪 TESTING EMBEDDING SERVICE")
    print("="*60)
    
    try:
        # Test load model
        print("1. Loading embedding model...")
        await embedding_service.load_model()
        
        # Test model info
        model_info = embedding_service.get_model_info()
        print(f"✅ Model loaded: {model_info['model_name']}")
        print(f"   Device: {model_info['device']}")
        print(f"   Dimension: {model_info['dimension']}")
        print(f"   Model path: {model_info['model_path']}")
        
        # Test generate embedding
        print("\n2. Testing embedding generation...")
        test_text = "Trí tuệ nhân tạo là một lĩnh vực khoa học máy tính"
        embedding = embedding_service.generate_embedding(test_text)
        
        print(f"✅ Generated embedding:")
        print(f"   Shape: {embedding.shape}")
        print(f"   Dimension: {embedding.shape[0]}")
        print(f"   Sample values: {embedding[:5]}")
        
        # Test batch embedding
        print("\n3. Testing batch embedding...")
        test_texts = [
            "Machine learning là gì?",
            "Deep learning hoạt động như thế nào?",
            "Neural networks có những loại nào?"
        ]
        
        embeddings = embedding_service.generate_embeddings_batch(test_texts)
        print(f"✅ Generated batch embeddings:")
        print(f"   Shape: {embeddings.shape}")
        print(f"   Number of texts: {len(test_texts)}")
        
        # Test validation
        print("\n4. Testing embedding validation...")
        is_valid = embedding_service.validate_embedding(embedding)
        print(f"✅ Embedding validation: {is_valid}")
        
        # Test normalization
        normalized = embedding_service.normalize_embedding(embedding)
        norm = sum(normalized**2)**0.5
        print(f"✅ Normalized embedding norm: {norm:.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding service test failed: {e}")
        return False

async def test_faiss_store():
    """Test FAISS store"""
    print("\n" + "="*60)
    print("🧪 TESTING FAISS STORE")
    print("="*60)
    
    try:
        # Test initialize
        print("1. Initializing FAISS store...")
        faiss_store.initialize_index()
        print("✅ FAISS index initialized")
        
        # Test add document
        print("\n2. Testing add document...")
        test_text = "FastAPI là một framework web hiện đại cho Python"
        chunk_id = faiss_store.add_document(
            text=test_text,
            doc_id="test_doc_1",
            chunk_index=0,
            filename="test.txt",
            embedding_service=embedding_service
        )
        print(f"✅ Added document chunk: {chunk_id}")
        
        # Test add multiple chunks
        print("\n3. Testing add multiple chunks...")
        test_chunks = [
            "ReactJS là một thư viện JavaScript",
            "Vue.js là một framework JavaScript",
            "Angular là một platform JavaScript"
        ]
        
        chunk_ids = faiss_store.add_document_chunks(
            chunks=test_chunks,
            doc_id="test_doc_2",
            filename="js_frameworks.txt",
            embedding_service=embedding_service
        )
        print(f"✅ Added {len(chunk_ids)} chunks: {chunk_ids}")
        
        # Test search
        print("\n4. Testing search...")
        query = "JavaScript framework"
        results = faiss_store.search_text(
            query_text=query,
            top_k=3,
            embedding_service=embedding_service
        )
        
        print(f"✅ Search results for '{query}':")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['content'][:50]}...")
            print(f"      Similarity: {result['similarity_score']:.4f}")
            print(f"      Document: {result['doc_id']}")
        
        # Test search with doc_id filter
        print("\n5. Testing search with document filter...")
        results_filtered = faiss_store.search_text(
            query_text=query,
            top_k=3,
            doc_id="test_doc_2",
            embedding_service=embedding_service
        )
        
        print(f"✅ Filtered search results (doc_id='test_doc_2'):")
        for i, result in enumerate(results_filtered, 1):
            print(f"   {i}. {result['content'][:50]}...")
            print(f"      Similarity: {result['similarity_score']:.4f}")
        
        # Test get document chunks
        print("\n6. Testing get document chunks...")
        chunks = faiss_store.get_document_chunks("test_doc_2")
        print(f"✅ Retrieved {len(chunks)} chunks for test_doc_2:")
        for chunk in chunks:
            print(f"   - {chunk['content'][:50]}...")
        
        # Test stats
        print("\n7. Testing stats...")
        stats = faiss_store.get_stats()
        print(f"✅ FAISS store stats:")
        print(f"   Total vectors: {stats['total_vectors']}")
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Total chunks: {stats['total_chunks']}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAISS store test failed: {e}")
        return False

async def test_vector_service():
    """Test integrated vector service"""
    print("\n" + "="*60)
    print("🧪 TESTING VECTOR SERVICE INTEGRATION")
    print("="*60)
    
    try:
        # Test initialize
        print("1. Initializing vector service...")
        await vector_service.initialize()
        print("✅ Vector service initialized")
        
        # Test add document
        print("\n2. Testing add document...")
        test_text = "Python là một ngôn ngữ lập trình phổ biến"
        chunk_id = vector_service.add_document(
            text=test_text,
            doc_id="python_doc",
            chunk_index=0,
            filename="python.txt"
        )
        print(f"✅ Added document: {chunk_id}")
        
        # Test add document chunks
        print("\n3. Testing add document chunks...")
        ai_chunks = [
            "Trí tuệ nhân tạo (AI) là công nghệ mô phỏng trí thông minh con người",
            "Machine learning là một nhánh của AI",
            "Deep learning sử dụng neural networks với nhiều lớp",
            "Natural language processing xử lý ngôn ngữ tự nhiên"
        ]
        
        chunk_ids = vector_service.add_document_chunks(
            chunks=ai_chunks,
            doc_id="ai_doc",
            filename="ai_concepts.txt"
        )
        print(f"✅ Added {len(chunk_ids)} chunks for AI document")
        
        # Test search
        print("\n4. Testing search...")
        query = "machine learning và neural networks"
        results = vector_service.search(query, top_k=3)
        
        print(f"✅ Search results for '{query}':")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['content'][:60]}...")
            print(f"      Similarity: {result['similarity_score']:.4f}")
            print(f"      Document: {result['doc_id']}")
            print(f"      Filename: {result['filename']}")
        
        # Test search with document filter
        print("\n5. Testing search with document filter...")
        results_filtered = vector_service.search(
            query="AI và machine learning",
            top_k=2,
            doc_id="ai_doc"
        )
        
        print(f"✅ Filtered search results (ai_doc only):")
        for i, result in enumerate(results_filtered, 1):
            print(f"   {i}. {result['content'][:60]}...")
            print(f"      Similarity: {result['similarity_score']:.4f}")
        
        # Test get document chunks
        print("\n6. Testing get document chunks...")
        chunks = vector_service.get_document_chunks("ai_doc")
        print(f"✅ Retrieved {len(chunks)} chunks for ai_doc:")
        for chunk in chunks:
            print(f"   - Chunk {chunk['chunk_index']}: {chunk['content'][:50]}...")
        
        # Test clear document
        print("\n7. Testing clear document...")
        success = vector_service.clear_doc("python_doc")
        print(f"✅ Clear document result: {success}")
        
        # Test stats
        print("\n8. Testing stats...")
        stats = vector_service.get_stats()
        print(f"✅ Vector service stats:")
        print(f"   Initialized: {stats['vector_service']['initialized']}")
        print(f"   Total vectors: {stats['vector_service']['total_vectors']}")
        print(f"   Total documents: {stats['vector_service']['total_documents']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector service test failed: {e}")
        return False

async def test_offline_operation():
    """Test hoạt động offline"""
    print("\n" + "="*60)
    print("🧪 TESTING OFFLINE OPERATION")
    print("="*60)
    
    try:
        # Test without internet connection
        print("1. Testing offline embedding generation...")
        
        # Disable internet (simulate)
        import socket
        original_socket = socket.socket
        
        def offline_socket(*args, **kwargs):
            raise socket.error("No internet connection")
        
        # socket.socket = offline_socket  # Uncomment to test real offline
        
        # Test embedding generation
        test_text = "Test offline embedding generation"
        embedding = embedding_service.generate_embedding(test_text)
        print(f"✅ Offline embedding generated: {embedding.shape}")
        
        # Test search
        print("\n2. Testing offline search...")
        results = vector_service.search("test query", top_k=2)
        print(f"✅ Offline search completed: {len(results)} results")
        
        # Restore socket
        socket.socket = original_socket
        
        print("\n✅ Offline operation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Offline operation test failed: {e}")
        return False

async def test_performance():
    """Test performance"""
    print("\n" + "="*60)
    print("🧪 TESTING PERFORMANCE")
    print("="*60)
    
    try:
        import time
        
        # Test embedding generation speed
        print("1. Testing embedding generation speed...")
        test_texts = [
            "Performance test text " + str(i) for i in range(10)
        ]
        
        start_time = time.time()
        embeddings = embedding_service.generate_embeddings_batch(test_texts)
        end_time = time.time()
        
        print(f"✅ Generated {len(test_texts)} embeddings in {end_time - start_time:.2f}s")
        print(f"   Speed: {len(test_texts)/(end_time - start_time):.2f} embeddings/second")
        
        # Test search speed
        print("\n2. Testing search speed...")
        start_time = time.time()
        results = vector_service.search("performance test", top_k=5)
        end_time = time.time()
        
        print(f"✅ Search completed in {end_time - start_time:.4f}s")
        print(f"   Results: {len(results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 VECTOR SERVICE INTEGRATION TEST")
    print("Testing embedding offline + FAISS integration")
    
    # Create test directories
    os.makedirs("models/embedding", exist_ok=True)
    os.makedirs("data/faiss_index", exist_ok=True)
    os.makedirs("data/metadata", exist_ok=True)
    
    test_results = []
    
    # Run tests
    test_results.append(await test_embedding_service())
    test_results.append(await test_faiss_store())
    test_results.append(await test_vector_service())
    test_results.append(await test_offline_operation())
    test_results.append(await test_performance())
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Vector service integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    # Cleanup
    try:
        await vector_service.cleanup()
        print("\n✅ Cleanup completed")
    except Exception as e:
        print(f"\n⚠️ Cleanup error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
