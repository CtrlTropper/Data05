# Vector Integration - Embedding Offline + FAISS

Hệ thống tích hợp embedding offline với FAISS vector database cho RAG chatbot.

## 🎯 **TỔNG QUAN**

Hệ thống cung cấp:
- ✅ **Embedding Service**: Load `intfloat/multilingual-e5-large` từ local
- ✅ **FAISS Store**: Vector database với tìm kiếm nhanh
- ✅ **Vector Service**: Tích hợp embedding + FAISS
- ✅ **Offline Operation**: Hoạt động hoàn toàn offline
- ✅ **Document Management**: Thêm, xóa, tìm kiếm documents

## 🏗️ **KIẾN TRÚC**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Vector Service │    │ Embedding       │    │ FAISS Store     │
│  (Integration)  │◄──►│ Service         │◄──►│ (Vector DB)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Routes    │    │  Local Model    │    │  Vector Index   │
│   (FastAPI)     │    │  (Offline)      │    │  (Persistent)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 **CẤU TRÚC FILES**

```
backend/
├── services/
│   ├── embedding_service.py    # Embedding service offline
│   └── vector_service.py       # Vector service integration
├── db/
│   └── faiss_store.py          # FAISS vector store
├── models/
│   └── embedding/              # Local embedding model
├── data/
│   ├── faiss_index/           # FAISS index files
│   └── metadata/              # Metadata files
├── test_vector_integration.py # Test script
├── setup_embedding_model.py   # Setup script
└── README_VECTOR_INTEGRATION.md
```

## 🚀 **CÀI ĐẶT VÀ SỬ DỤNG**

### **1. Cài đặt Dependencies**
```bash
pip install sentence-transformers torch faiss-cpu numpy
```

### **2. Tải Embedding Model**
```bash
# Tải model intfloat/multilingual-e5-large về local
python setup_embedding_model.py
```

### **3. Test Integration**
```bash
# Test toàn bộ hệ thống
python test_vector_integration.py
```

## 🔧 **API SỬ DỤNG**

### **Vector Service**

```python
from services.vector_service import vector_service

# Khởi tạo
await vector_service.initialize()

# Thêm document
chunk_id = vector_service.add_document(
    text="Nội dung text",
    doc_id="doc_1",
    chunk_index=0,
    filename="document.txt"
)

# Thêm nhiều chunks
chunk_ids = vector_service.add_document_chunks(
    chunks=["chunk 1", "chunk 2", "chunk 3"],
    doc_id="doc_2",
    filename="document.txt"
)

# Tìm kiếm
results = vector_service.search(
    query="câu hỏi tìm kiếm",
    top_k=5,
    doc_id=None  # None = tìm toàn bộ, hoặc "doc_1" để tìm trong doc cụ thể
)

# Xóa document
success = vector_service.clear_doc("doc_1")

# Lấy chunks của document
chunks = vector_service.get_document_chunks("doc_1")

# Thống kê
stats = vector_service.get_stats()

# Cleanup
await vector_service.cleanup()
```

### **Embedding Service**

```python
from services.embedding_service import embedding_service

# Khởi tạo
await embedding_service.load_model()

# Tạo embedding
embedding = embedding_service.generate_embedding("text cần embedding")

# Tạo batch embeddings
embeddings = embedding_service.generate_embeddings_batch([
    "text 1", "text 2", "text 3"
])

# Thông tin model
info = embedding_service.get_model_info()

# Cleanup
await embedding_service.cleanup()
```

### **FAISS Store**

```python
from db.faiss_store import faiss_store

# Khởi tạo
faiss_store.initialize_index()

# Load index
faiss_store.load_index()

# Thêm document
chunk_id = faiss_store.add_document(
    text="text content",
    doc_id="doc_1",
    chunk_index=0,
    filename="file.txt",
    embedding_service=embedding_service
)

# Tìm kiếm
results = faiss_store.search_text(
    query_text="search query",
    top_k=5,
    doc_id=None,
    embedding_service=embedding_service
)

# Xóa document
success = faiss_store.clear_doc("doc_1")

# Lưu index
faiss_store.save_index()
```

## 📊 **TÍNH NĂNG CHÍNH**

### **1. Embedding Service**
- ✅ **Offline Operation**: Load model từ local, không cần internet
- ✅ **Multilingual Support**: Hỗ trợ đa ngôn ngữ (Việt, Anh, etc.)
- ✅ **Batch Processing**: Xử lý nhiều text cùng lúc
- ✅ **Normalization**: Chuẩn hóa vectors cho cosine similarity
- ✅ **Validation**: Kiểm tra tính hợp lệ của embeddings

### **2. FAISS Store**
- ✅ **Fast Search**: Tìm kiếm vector nhanh với FAISS
- ✅ **Persistent Storage**: Lưu trữ index và metadata
- ✅ **Document Management**: Quản lý documents và chunks
- ✅ **Filtering**: Tìm kiếm trong document cụ thể
- ✅ **Backup/Restore**: Sao lưu và khôi phục dữ liệu

### **3. Vector Service**
- ✅ **Integration**: Tích hợp embedding + FAISS
- ✅ **Text Chunking**: Chia text thành chunks
- ✅ **Error Handling**: Xử lý lỗi robust
- ✅ **Statistics**: Thống kê chi tiết
- ✅ **Async Support**: Hỗ trợ async/await

## 🧪 **TESTING**

### **Test Scripts**

```bash
# Test embedding service
python -c "
import asyncio
from services.embedding_service import embedding_service

async def test():
    await embedding_service.load_model()
    embedding = embedding_service.generate_embedding('test text')
    print(f'Embedding shape: {embedding.shape}')

asyncio.run(test())
"

# Test FAISS store
python -c "
from db.faiss_store import faiss_store
from services.embedding_service import embedding_service

faiss_store.initialize_index()
chunk_id = faiss_store.add_document(
    'test content', 'test_doc', 0, 'test.txt', embedding_service
)
print(f'Added chunk: {chunk_id}')
"

# Test vector service
python -c "
import asyncio
from services.vector_service import vector_service

async def test():
    await vector_service.initialize()
    chunk_id = vector_service.add_document('test', 'doc1', 0, 'test.txt')
    results = vector_service.search('test query', 5)
    print(f'Search results: {len(results)}')

asyncio.run(test())
"
```

### **Full Integration Test**
```bash
python test_vector_integration.py
```

## 📈 **PERFORMANCE**

### **Benchmarks**
- **Embedding Generation**: ~100-500ms per text
- **Batch Embedding**: ~50-200ms per text (batch size 8)
- **FAISS Search**: ~1-10ms per query
- **Document Addition**: ~200-1000ms per document
- **Memory Usage**: ~2-4GB RAM (model + index)

### **Optimization Tips**
- Sử dụng batch processing cho nhiều texts
- Chia documents thành chunks hợp lý (500-1000 chars)
- Sử dụng GPU nếu có (CUDA)
- Regular backup FAISS index

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

#### **1. Model Not Found**
```
FileNotFoundError: Embedding model not found
```
**Solution**: Chạy `python setup_embedding_model.py` để tải model

#### **2. CUDA Out of Memory**
```
RuntimeError: CUDA out of memory
```
**Solution**: Sử dụng CPU hoặc giảm batch size

#### **3. FAISS Index Corrupted**
```
RuntimeError: FAISS index corrupted
```
**Solution**: Xóa `data/faiss_index/` và tạo lại

#### **4. Embedding Dimension Mismatch**
```
ValueError: Invalid embedding dimension
```
**Solution**: Kiểm tra model version và dimension

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
```

## 📝 **CONFIGURATION**

### **Environment Variables**
```bash
# Model paths
EMBEDDING_MODEL_PATH=models/embedding
FAISS_INDEX_PATH=data/faiss_index
FAISS_METADATA_PATH=data/metadata

# Performance settings
EMBEDDING_BATCH_SIZE=8
FAISS_INDEX_TYPE=IndexFlatIP
EMBEDDING_DIMENSION=1024
```

### **Model Configuration**
```python
# Trong embedding_service.py
class EmbeddingService:
    def __init__(self, model_path="models/embedding"):
        self.model_path = model_path
        self.dimension = 1024  # multilingual-e5-large
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
```

## 🚀 **DEPLOYMENT**

### **Production Setup**
```bash
# 1. Tải model
python setup_embedding_model.py

# 2. Test integration
python test_vector_integration.py

# 3. Start FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000
```

### **Docker**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python setup_embedding_model.py

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🎉 **KẾT LUẬN**

Hệ thống Vector Integration đã hoàn thiện với:

- ✅ **Offline Embedding**: multilingual-e5-large từ local
- ✅ **FAISS Vector Store**: Tìm kiếm nhanh và persistent
- ✅ **Complete Integration**: Vector Service tích hợp hoàn chỉnh
- ✅ **Production Ready**: Error handling và performance optimization
- ✅ **Comprehensive Testing**: Test suite đầy đủ

Hệ thống sẵn sàng cho production với khả năng hoạt động hoàn toàn offline!
