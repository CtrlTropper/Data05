"""
Test script cho search functionality
"""

import asyncio
import numpy as np
from services.embedding_service import embedding_service
from db.faiss_store import faiss_store

async def test_search_functionality():
    """Test các chức năng search"""
    
    print("🧪 Testing Search Functionality...")
    
    # Test 1: Load embedding service
    print("\n1. Loading embedding service...")
    await embedding_service.load_model()
    print("✅ Embedding service loaded")
    
    # Test 2: Generate test embeddings
    print("\n2. Generating test embeddings...")
    test_texts = [
        "Đây là đoạn văn bản về công nghệ AI",
        "Machine learning là một phần của trí tuệ nhân tạo",
        "Deep learning sử dụng neural networks",
        "Natural language processing xử lý ngôn ngữ tự nhiên",
        "Computer vision nhận diện hình ảnh"
    ]
    
    embeddings = embedding_service.generate_embeddings_batch(test_texts)
    print(f"✅ Generated {len(embeddings)} embeddings")
    
    # Test 3: Add vectors to FAISS
    print("\n3. Adding vectors to FAISS...")
    vectors_array = np.array(embeddings, dtype=np.float32)
    
    metadata_list = []
    for i, text in enumerate(test_texts):
        metadata = {
            "document_id": "test_doc_1",
            "chunk_id": f"test_chunk_{i}",
            "chunk_index": i,
            "content": text,
            "content_length": len(text),
            "filename": "test_document.txt"
        }
        metadata_list.append(metadata)
    
    vector_ids = faiss_store.add_vectors(vectors_array, metadata_list)
    print(f"✅ Added {len(vector_ids)} vectors to FAISS")
    
    # Test 4: Search with text
    print("\n4. Testing text search...")
    query_text = "trí tuệ nhân tạo và machine learning"
    results = faiss_store.search_text(
        query_text=query_text,
        top_k=3,
        embedding_service=embedding_service
    )
    
    print(f"Query: {query_text}")
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. Score: {result['similarity_score']:.4f}")
        print(f"     Content: {result['content']}")
        print(f"     Document: {result['document_id']}")
    
    # Test 5: Search with vector
    print("\n5. Testing vector search...")
    query_embedding = embedding_service.generate_embedding("neural networks và deep learning")
    query_vector = np.array(query_embedding, dtype=np.float32)
    
    results = faiss_store.search_with_context(
        query_vector=query_vector,
        top_k=2
    )
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. Score: {result['similarity_score']:.4f}")
        print(f"     Content: {result['content']}")
    
    # Test 6: Search with document filter
    print("\n6. Testing document filter...")
    results = faiss_store.search_text(
        query_text="AI technology",
        top_k=5,
        doc_id="test_doc_1",
        embedding_service=embedding_service
    )
    
    print(f"Found {len(results)} results in test_doc_1:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. Score: {result['similarity_score']:.4f}")
        print(f"     Content: {result['content']}")
    
    # Test 7: Get document contexts
    print("\n7. Testing get document contexts...")
    contexts = faiss_store.get_contexts_by_document("test_doc_1")
    print(f"Found {len(contexts)} contexts in test_doc_1:")
    for i, context in enumerate(contexts, 1):
        print(f"  {i}. Chunk {context['chunk_index']}: {context['content']}")
    
    # Test 8: Search similar contexts
    print("\n8. Testing similar contexts search...")
    results = faiss_store.search_similar_contexts(
        context_text="computer vision và image recognition",
        top_k=3,
        embedding_service=embedding_service
    )
    
    print(f"Found {len(results)} similar contexts:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. Score: {result['similarity_score']:.4f}")
        print(f"     Content: {result['content']}")
    
    # Test 9: Get stats
    print("\n9. Testing stats...")
    stats = faiss_store.get_stats()
    print("FAISS Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_search_functionality())
