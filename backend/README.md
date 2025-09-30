# RAG + LLM Chatbot Backend

Backend API cho hệ thống chatbot RAG + LLM hoạt động hoàn toàn offline.

## 🏗️ Cấu trúc dự án

```
backend/
├── main.py                 # FastAPI app chính
├── requirements.txt        # Dependencies
├── env.example            # Environment variables example
├── routers/               # API routes
│   ├── __init__.py
│   ├── health.py          # Health check endpoints
│   ├── documents.py       # Document management endpoints
│   └── chat.py           # Chat endpoints
├── services/              # Business logic
│   ├── __init__.py
│   ├── config.py         # Configuration settings
│   ├── model_manager.py  # AI models management
│   ├── document_service.py # Document processing
│   └── rag_service.py    # RAG logic
├── models/               # Data models
│   ├── __init__.py
│   ├── schemas.py        # Pydantic schemas
│   └── database.py       # SQLAlchemy models
└── db/                   # Database layer
    ├── __init__.py
    ├── database.py       # Database connection
    └── vector_db.py      # FAISS vector database
```

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình environment

```bash
cp env.example .env
# Chỉnh sửa .env theo cấu hình của bạn
```

### 3. Tạo thư mục cần thiết

```bash
mkdir -p data/faiss_index
mkdir -p data/metadata
mkdir -p uploads
mkdir -p models
```

### 4. Chạy ứng dụng

```bash
# Development mode
python main.py

# Hoặc sử dụng uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API Endpoints

### Health Check
- `GET /api/health` - Kiểm tra trạng thái hệ thống
- `GET /api/health/detailed` - Kiểm tra chi tiết các component

### Document Management
- `POST /api/documents/upload` - Upload tài liệu
- `GET /api/documents` - Lấy danh sách tài liệu
- `GET /api/documents/{id}` - Lấy thông tin tài liệu
- `DELETE /api/documents/{id}` - Xóa tài liệu
- `POST /api/documents/{id}/process` - Xử lý tài liệu
- `GET /api/documents/{id}/chunks` - Lấy chunks của tài liệu

### Chat
- `POST /api/chat` - Chat với hệ thống RAG
- `POST /api/chat/document/{id}` - Chat với tài liệu cụ thể
- `GET /api/chat/history/{session_id}` - Lấy lịch sử chat
- `DELETE /api/chat/history/{session_id}` - Xóa lịch sử chat
- `GET /api/chat/sessions` - Lấy danh sách sessions

## 🔧 Cấu hình

### Environment Variables

- `EMBEDDING_MODEL_PATH`: Đường dẫn đến model embedding
- `LLM_MODEL_PATH`: Đường dẫn đến model LLM
- `FAISS_INDEX_PATH`: Đường dẫn lưu FAISS index
- `UPLOAD_DIR`: Thư mục upload files
- `MAX_FILE_SIZE`: Kích thước file tối đa
- `DEFAULT_CHUNK_SIZE`: Kích thước chunk mặc định
- `DEFAULT_TOP_K`: Số chunks liên quan mặc định

## 🧠 AI Models

### Embedding Model
- **Model**: `intfloat/multilingual-e5-large`
- **Dimension**: 768
- **Usage**: Tạo embeddings cho documents và queries

### LLM Model
- **Model**: `gpt-oss-20b`
- **Usage**: Generate responses dựa trên context

## 💾 Database

### SQLite Database
- Lưu trữ metadata của documents, chunks, chat sessions
- File: `data/chatbot.db`

### FAISS Vector Database
- Lưu trữ vector embeddings
- Index type: `IndexFlatIP` (cosine similarity)
- Files: `data/faiss_index/faiss_index.bin`, `metadata.pkl`

## 🔄 Flow xử lý

### Upload Document
1. Upload file → Validate → Save to disk
2. Parse content → Chunk text → Generate embeddings
3. Store in FAISS → Update metadata

### Chat Process
1. User query → Generate embedding
2. Search FAISS → Get relevant chunks
3. Create context → Generate response with LLM
4. Return response with sources

## 🛠️ Development

### Chạy tests
```bash
pytest
```

### Code formatting
```bash
black .
isort .
```

### Type checking
```bash
mypy .
```

## 📝 Notes

- Tất cả models hoạt động offline, không cần internet
- FAISS index được tự động save/load
- Hỗ trợ multiple document types: PDF, DOCX, TXT, MD
- Có thể chat với toàn bộ documents hoặc một document cụ thể
