# RAG + LLM Chatbot System - Hướng dẫn hoàn chỉnh

Hệ thống chatbot RAG + LLM hoạt động hoàn toàn offline với FastAPI backend.

## 🎯 **TỔNG QUAN HỆ THỐNG**

### **Kiến trúc**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Models     │
│   (ReactJS)     │◄──►│   (FastAPI)     │◄──►│   (Offline)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Vector DB      │
                    │  (FAISS)        │
                    └─────────────────┘
```

### **Các Module chính**
- ✅ **Documents**: Upload, quản lý tài liệu
- ✅ **Embedding**: Tạo embeddings từ tài liệu
- ✅ **Search**: Tìm kiếm vector với FAISS
- ✅ **Chat**: Chatbot RAG + LLM
- ✅ **Health**: Kiểm tra trạng thái hệ thống

## 🚀 **CÀI ĐẶT VÀ KHỞI CHẠY**

### **1. Cài đặt Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **2. Tải Models (Lần đầu)**
```bash
# Tải các AI models
python setup_models.py
```

### **3. Khởi chạy hệ thống**
```bash
# Cách 1: Sử dụng script khởi chạy
python start.py

# Cách 2: Chạy trực tiếp
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **4. Kiểm tra hệ thống**
```bash
# Test toàn bộ hệ thống
python test_full_system.py
```

## 📚 **API ENDPOINTS**

### **Health Check**
- `GET /api/health` - Kiểm tra trạng thái hệ thống

### **Document Management**
- `POST /api/documents/upload` - Upload tài liệu
- `GET /api/documents` - Lấy danh sách tài liệu
- `GET /api/documents/{id}` - Lấy thông tin tài liệu
- `DELETE /api/documents/{id}` - Xóa tài liệu
- `POST /api/documents/{id}/select` - Chọn tài liệu

### **Embedding System**
- `POST /api/embed/document/{id}` - Tạo embeddings cho tài liệu
- `POST /api/embed/text` - Tạo embedding cho text
- `GET /api/embed/stats` - Thống kê embedding

### **Search System**
- `POST /api/search/text` - Tìm kiếm bằng text
- `POST /api/search/vector` - Tìm kiếm bằng vector
- `GET /api/search/document/{id}` - Lấy contexts của document
- `GET /api/search/stats` - Thống kê search

### **Chat System**
- `POST /api/chat` - Chat cơ bản
- `POST /api/chat/document/{id}` - Chat với document
- `POST /api/chat/stream` - Streaming chat
- `GET /api/chat/stats` - Thống kê chat

## 🔧 **CẤU TRÚC DỰ ÁN**

```
backend/
├── main.py                 # FastAPI app chính
├── start.py               # Script khởi chạy
├── setup_models.py        # Script tải models
├── test_full_system.py    # Test toàn bộ hệ thống
├── requirements.txt       # Dependencies
├── env.example           # Environment variables
├── routers/              # API routes
│   ├── health.py         # Health check
│   ├── documents.py      # Document management
│   ├── embedding.py      # Embedding system
│   ├── search.py         # Search system
│   └── chat.py          # Chat system
├── services/             # Business logic
│   ├── config.py         # Configuration
│   ├── embedding_service.py # Embedding service
│   ├── llm_service.py    # LLM service
│   ├── model_manager.py  # Model manager
│   ├── document_service.py # Document service
│   └── rag_service.py    # RAG service
├── models/               # Data models
│   ├── schemas.py        # Pydantic schemas
│   └── database.py       # SQLAlchemy models
├── db/                   # Database layer
│   ├── database.py       # Database connection
│   ├── faiss_store.py    # FAISS vector store
│   └── vector_db.py      # Vector database
├── data/                 # Data storage
│   ├── docs/            # Documents
│   ├── faiss_store/     # FAISS index
│   ├── metadata/        # Metadata
│   └── documents_metadata.json
├── models/               # AI Models
│   ├── embedding/       # Embedding model
│   └── llm/            # LLM model
└── uploads/             # Upload directory
```

## 🧪 **TESTING**

### **1. Test từng module**
```bash
# Test search
python test_search.py

# Test chat
python test_chat.py
```

### **2. Test toàn bộ hệ thống**
```bash
# Test tích hợp
python test_full_system.py
```

### **3. Manual testing**
```bash
# Health check
curl http://localhost:8000/api/health

# Upload document
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.txt"

# Chat
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "Trí tuệ nhân tạo là gì?"}'
```

## 📊 **WORKFLOW SỬ DỤNG**

### **1. Upload và xử lý tài liệu**
```bash
# 1. Upload document
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.txt"

# 2. Tạo embeddings
curl -X POST "http://localhost:8000/api/embed/document/{doc_id}" \
  -H "Content-Type: application/json" \
  -d '{"chunk_size": 500, "chunk_overlap": 50}'
```

### **2. Chat với tài liệu**
```bash
# Chat với toàn bộ documents
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "Nội dung chính là gì?", "top_k": 5}'

# Chat với document cụ thể
curl -X POST "http://localhost:8000/api/chat/document/{doc_id}" \
  -H "Content-Type: application/json" \
  -d '{"question": "Tóm tắt tài liệu này"}'
```

### **3. Tìm kiếm**
```bash
# Tìm kiếm text
curl -X POST "http://localhost:8000/api/search/text" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 5}'
```

## ⚡ **PERFORMANCE**

### **Benchmarks**
- **Document Upload**: ~1-5s (tùy kích thước)
- **Embedding Creation**: ~10-30s (tùy số chunks)
- **Search**: ~100-500ms
- **Chat**: ~2-8s (bao gồm LLM generation)
- **Streaming Chat**: ~1-3s (first token)

### **Memory Requirements**
- **RAM**: Tối thiểu 16GB
- **VRAM**: Khuyến nghị 12GB+ (nếu dùng GPU)
- **Storage**: ~50GB cho models

## 🔍 **TROUBLESHOOTING**

### **1. Models không load được**
```bash
# Kiểm tra thư mục models
ls -la models/embedding/
ls -la models/llm/

# Tải lại models
python setup_models.py
```

### **2. Dependencies lỗi**
```bash
# Cài đặt lại dependencies
pip install -r requirements.txt

# Hoặc sử dụng script khởi chạy
python start.py
```

### **3. Server không start**
```bash
# Kiểm tra port 8000
netstat -an | grep 8000

# Chạy với port khác
uvicorn main:app --port 8001 --reload
```

### **4. Memory issues**
```bash
# Kiểm tra RAM usage
htop

# Restart server
python start.py
```

## 📝 **CONFIGURATION**

### **Environment Variables**
```bash
# Copy và chỉnh sửa
cp env.example .env

# Các biến quan trọng
EMBEDDING_MODEL_PATH=models/embedding
LLM_MODEL_PATH=models/llm
FAISS_INDEX_PATH=data/faiss_store
MAX_FILE_SIZE=52428800
DEFAULT_CHUNK_SIZE=500
DEFAULT_TOP_K=5
```

### **Model Configuration**
```python
# Trong services/config.py
EMBEDDING_MODEL_PATH = "models/embedding"
LLM_MODEL_PATH = "models/llm"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_TOP_K = 5
MAX_TOKENS = 1000
TEMPERATURE = 0.7
```

## 🎯 **TÍNH NĂNG NỔI BẬT**

### **Offline Operation**
- ✅ Hoàn toàn offline, không cần internet
- ✅ Models load từ local storage
- ✅ Không gọi external APIs

### **RAG System**
- ✅ Retrieval-Augmented Generation
- ✅ Vector search với FAISS
- ✅ Context-aware responses
- ✅ Source tracking

### **Multi-document Support**
- ✅ Upload multiple documents
- ✅ Document-specific chat
- ✅ Global search across documents
- ✅ Document selection

### **Performance**
- ✅ Fast vector search
- ✅ Streaming responses
- ✅ Batch processing
- ✅ Memory optimization

## 🚀 **DEPLOYMENT**

### **Development**
```bash
python start.py
```

### **Production**
```bash
# Sử dụng gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### **Docker**
```bash
# Build image
docker build -t rag-chatbot .

# Run container
docker run -p 8000:8000 rag-chatbot
```

## 📞 **SUPPORT**

### **Logs**
```bash
# Xem logs
tail -f logs/app.log

# Debug mode
DEBUG=true python start.py
```

### **API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### **Health Check**
```bash
curl http://localhost:8000/api/health
```

---

**🎉 Hệ thống RAG + LLM Chatbot đã sẵn sàng sử dụng!**
