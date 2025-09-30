# Search Module - Hướng dẫn sử dụng

Module tìm kiếm vector bằng FAISS với các tính năng tìm kiếm context và filter theo document.

## 🎯 **TÍNH NĂNG CHÍNH**

### **1. Tìm kiếm cơ bản**
- ✅ `search(query, top_k=5, doc_id=None)` - Tìm kiếm vector
- ✅ Hỗ trợ filter theo document ID
- ✅ Trả về danh sách context (đoạn text gần nhất)
- ✅ Cosine similarity với FAISS IndexFlatIP

### **2. Các loại tìm kiếm**
- ✅ **Text Search**: Tìm kiếm bằng text query
- ✅ **Vector Search**: Tìm kiếm bằng vector
- ✅ **Document Filter**: Tìm kiếm trong document cụ thể
- ✅ **Similar Contexts**: Tìm contexts tương tự

## 📚 **API ENDPOINTS**

### **1. Text Search**
```http
POST /api/search/text
Content-Type: application/json

{
    "query": "trí tuệ nhân tạo và machine learning",
    "top_k": 5,
    "doc_id": "document_uuid"  // optional
}
```

**Response:**
```json
{
    "query": "trí tuệ nhân tạo và machine learning",
    "results": [
        {
            "content": "Machine learning là một phần của trí tuệ nhân tạo",
            "similarity_score": 0.95,
            "document_id": "doc_uuid",
            "chunk_id": "doc_uuid_chunk_1",
            "chunk_index": 1,
            "filename": "document.txt",
            "content_length": 45,
            "created_at": "2024-01-01T10:00:00"
        }
    ],
    "total_found": 1,
    "search_time": 0.123
}
```

### **2. Vector Search**
```http
POST /api/search/vector
Content-Type: application/json

{
    "vector": [0.1, 0.2, 0.3, ...],  // 1024 dimensions
    "top_k": 5,
    "doc_id": "document_uuid"  // optional
}
```

### **3. Document Contexts**
```http
GET /api/search/document/{document_id}
```

### **4. Similar Contexts**
```http
POST /api/search/similar
Content-Type: application/json

{
    "query": "neural networks và deep learning",
    "top_k": 3
}
```

### **5. Embed and Search**
```http
POST /api/search/embed
Content-Type: application/json

{
    "query": "computer vision",
    "top_k": 5
}
```

## 🔧 **SỬ DỤNG TRONG CODE**

### **1. Tìm kiếm cơ bản**
```python
from db.faiss_store import faiss_store
from services.embedding_service import embedding_service

# Tìm kiếm bằng text
results = faiss_store.search_text(
    query_text="trí tuệ nhân tạo",
    top_k=5,
    embedding_service=embedding_service
)

# Tìm kiếm trong document cụ thể
results = faiss_store.search_text(
    query_text="machine learning",
    top_k=3,
    doc_id="document_uuid",
    embedding_service=embedding_service
)
```

### **2. Tìm kiếm bằng vector**
```python
import numpy as np

# Tạo embedding
embedding = embedding_service.generate_embedding("AI technology")
query_vector = np.array(embedding, dtype=np.float32)

# Tìm kiếm
results = faiss_store.search_with_context(
    query_vector=query_vector,
    top_k=5,
    doc_id="document_uuid"  # optional
)
```

### **3. Lấy contexts của document**
```python
# Lấy tất cả contexts của một document
contexts = faiss_store.get_contexts_by_document("document_uuid")

for context in contexts:
    print(f"Chunk {context['chunk_index']}: {context['content']}")
```

### **4. Tìm contexts tương tự**
```python
# Tìm contexts tương tự với một đoạn text
results = faiss_store.search_similar_contexts(
    context_text="deep learning và neural networks",
    top_k=3,
    embedding_service=embedding_service
)
```

## 🚀 **CÁCH SỬ DỤNG**

### **1. Test Search Functionality**
```bash
# Chạy test script
python test_search.py
```

### **2. API Testing**
```bash
# Text search
curl -X POST "http://localhost:8000/api/search/text" \
  -H "Content-Type: application/json" \
  -d '{"query": "trí tuệ nhân tạo", "top_k": 5}'

# Search in specific document
curl -X POST "http://localhost:8000/api/search/text" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 3, "doc_id": "document_uuid"}'

# Get document contexts
curl "http://localhost:8000/api/search/document/document_uuid"

# Search stats
curl "http://localhost:8000/api/search/stats"
```

## 📊 **CẤU TRÚC DỮ LIỆU**

### **Search Result Format**
```json
{
    "content": "Nội dung đoạn text",
    "similarity_score": 0.95,
    "document_id": "doc_uuid",
    "chunk_id": "doc_uuid_chunk_1",
    "chunk_index": 1,
    "filename": "document.txt",
    "content_length": 45,
    "created_at": "2024-01-01T10:00:00"
}
```

### **Search Response Format**
```json
{
    "query": "search query",
    "results": [...],
    "total_found": 5,
    "search_time": 0.123
}
```

## ⚡ **PERFORMANCE**

### **Tối ưu hóa**
- ✅ **Batch Search**: Tìm kiếm nhiều vectors cùng lúc
- ✅ **Document Filter**: Filter hiệu quả theo document_id
- ✅ **Vector Normalization**: Cosine similarity với FAISS
- ✅ **Memory Efficient**: Chỉ load metadata cần thiết

### **Benchmarks**
- **Text Search**: ~100-200ms (bao gồm embedding generation)
- **Vector Search**: ~10-50ms (chỉ FAISS search)
- **Document Filter**: ~20-100ms (tùy số lượng vectors)

## 🔍 **TÌM KIẾM NÂNG CAO**

### **1. Multi-document Search**
```python
# Tìm kiếm trong nhiều documents
doc_ids = ["doc1", "doc2", "doc3"]
all_results = []

for doc_id in doc_ids:
    results = faiss_store.search_text(
        query_text="AI technology",
        top_k=3,
        doc_id=doc_id,
        embedding_service=embedding_service
    )
    all_results.extend(results)

# Sort by similarity score
all_results.sort(key=lambda x: x['similarity_score'], reverse=True)
```

### **2. Context Aggregation**
```python
# Tổng hợp contexts từ nhiều chunks
def aggregate_contexts(results, max_length=2000):
    aggregated = ""
    for result in results:
        if len(aggregated) + len(result['content']) <= max_length:
            aggregated += result['content'] + "\n\n"
        else:
            break
    return aggregated.strip()
```

### **3. Similarity Threshold**
```python
# Filter theo similarity threshold
def filter_by_threshold(results, threshold=0.7):
    return [r for r in results if r['similarity_score'] >= threshold]
```

## 🐛 **TROUBLESHOOTING**

### **1. Không tìm thấy kết quả**
```bash
# Kiểm tra FAISS index
curl "http://localhost:8000/api/search/stats"

# Kiểm tra documents
curl "http://localhost:8000/api/documents"
```

### **2. Search chậm**
```bash
# Kiểm tra embedding service
curl "http://localhost:8000/api/embed/stats"

# Restart service
python main.py
```

### **3. Vector dimension lỗi**
```python
# Kiểm tra embedding dimension
embedding = embedding_service.generate_embedding("test")
print(f"Dimension: {len(embedding)}")  # Should be 1024
```

## 📝 **NOTES**

- **Vector Dimension**: 1024 (multilingual-e5-large)
- **Similarity Metric**: Cosine similarity
- **Index Type**: FAISS IndexFlatIP
- **Document Filter**: Hỗ trợ filter theo document_id
- **Context Format**: Trả về đầy đủ metadata
- **Performance**: Tối ưu cho search nhanh
- **Offline**: Hoàn toàn offline, không cần internet
