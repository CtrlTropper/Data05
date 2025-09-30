# Embedding Module - Hướng dẫn sử dụng

Module xử lý embedding offline cho hệ thống chatbot RAG + LLM.

## 🏗️ Cấu trúc Module

```
backend/
├── services/
│   └── embedding_service.py    # Service xử lý embedding
├── db/
│   └── faiss_store.py         # FAISS vector store
├── routers/
│   └── embedding.py           # API endpoints
└── models/
    └── embedding/             # Thư mục chứa model
```

## 🚀 Cài đặt Model

### 1. Tải model multilingual-e5-large

```bash
# Tạo thư mục
mkdir -p models/embedding

# Tải model (cần có internet lần đầu)
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('intfloat/multilingual-e5-large')
model.save('models/embedding')
print('Model downloaded successfully!')
"
```

### 2. Kiểm tra model

```bash
# Kiểm tra thư mục model
ls -la models/embedding/
# Nên có các file: config.json, pytorch_model.bin, tokenizer.json, etc.
```

## 📚 API Endpoints

### 1. Embed Document
```http
POST /api/embed/document/{document_id}
Content-Type: application/json

{
    "chunk_size": 500,
    "chunk_overlap": 50
}
```

**Response:**
```json
{
    "document_id": "uuid",
    "chunks_created": 25,
    "vectors_stored": 25,
    "processing_time": 12.5,
    "status": "success"
}
```

### 2. Embed Text
```http
POST /api/embed/text
Content-Type: application/json

{
    "text": "Đây là đoạn văn bản cần tạo embedding"
}
```

**Response:**
```json
{
    "embedding": [0.1, 0.2, 0.3, ...],
    "dimension": 1024,
    "text_length": 45
}
```

### 3. Get Embedding Stats
```http
GET /api/embed/stats
```

**Response:**
```json
{
    "faiss_store": {
        "total_vectors": 150,
        "dimension": 1024,
        "documents_count": 5,
        "index_size_mb": 0.6
    },
    "embedding_service": {
        "model_loaded": true,
        "model_path": "models/embedding",
        "device": "cpu",
        "dimension": 1024
    },
    "documents": {
        "total_documents": 5,
        "processed_documents": 3
    }
}
```

### 4. Delete Document Embeddings
```http
DELETE /api/embed/document/{document_id}
```

### 5. Get Document Vectors
```http
GET /api/embed/document/{document_id}/vectors
```

## 🔧 Sử dụng trong Code

### 1. Generate Embedding

```python
from services.embedding_service import embedding_service

# Tạo embedding cho text
text = "Đây là đoạn văn bản"
embedding = embedding_service.generate_embedding(text)
print(f"Embedding dimension: {len(embedding)}")
```

### 2. Batch Embeddings

```python
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = embedding_service.generate_embeddings_batch(texts)
print(f"Generated {len(embeddings)} embeddings")
```

### 3. FAISS Operations

```python
from db.faiss_store import faiss_store
import numpy as np

# Thêm vectors
vectors = np.array(embeddings, dtype=np.float32)
metadata = [{"document_id": "doc1", "content": "text1"}]
vector_ids = faiss_store.add_vectors(vectors, metadata)

# Tìm kiếm
query_vector = np.array([embedding], dtype=np.float32)
results = faiss_store.search(query_vector, k=5)
```

## 📊 Workflow Xử lý Document

### 1. Upload Document
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.txt"
```

### 2. Create Embeddings
```bash
curl -X POST "http://localhost:8000/api/embed/document/{document_id}" \
  -H "Content-Type: application/json" \
  -d '{"chunk_size": 500, "chunk_overlap": 50}'
```

### 3. Check Stats
```bash
curl "http://localhost:8000/api/embed/stats"
```

## 🗂️ Cấu trúc Dữ liệu

### FAISS Store
- **Index**: `data/faiss_store/faiss_index.bin`
- **Metadata**: `data/faiss_store/metadata.json`

### Metadata Format
```json
{
    "vector_id": "vec_0_abc123",
    "document_id": "doc_uuid",
    "chunk_id": "doc_uuid_chunk_0",
    "chunk_index": 0,
    "content": "Nội dung chunk...",
    "content_length": 500,
    "created_at": "2024-01-01T10:00:00",
    "filename": "document.txt",
    "index_id": 0
}
```

## ⚡ Performance Tips

### 1. Batch Processing
- Sử dụng `generate_embeddings_batch()` cho nhiều text
- Xử lý documents theo batch

### 2. Memory Management
- Model được load một lần và reuse
- FAISS index được cache trên disk
- GPU memory được cleanup khi shutdown

### 3. Chunking Strategy
- Chunk size: 500-1000 characters
- Overlap: 50-100 characters
- Tìm điểm cắt tự nhiên (dấu câu, xuống dòng)

## 🐛 Troubleshooting

### 1. Model không load được
```bash
# Kiểm tra thư mục model
ls -la models/embedding/

# Kiểm tra logs
tail -f logs/app.log
```

### 2. FAISS index lỗi
```bash
# Xóa và tạo lại index
rm -rf data/faiss_store/
mkdir -p data/faiss_store/
```

### 3. Memory issues
```bash
# Kiểm tra RAM usage
htop

# Restart service
python main.py
```

## 📝 Notes

- Model multilingual-e5-large có dimension 1024
- FAISS sử dụng cosine similarity (IndexFlatIP)
- Tất cả operations đều offline
- Metadata được lưu dưới dạng JSON
- Hỗ trợ batch processing cho performance tốt hơn
