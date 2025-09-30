# Chatbot Module - Hướng dẫn sử dụng

Module chatbot RAG + LLM hoạt động hoàn toàn offline với gpt-oss-20b.

## 🎯 **TÍNH NĂNG CHÍNH**

### **1. LLM Service**
- ✅ Load model `gpt-oss-20b` từ `./models/llm/` (offline)
- ✅ Hàm `generate_answer(question, context)` → trả về câu trả lời
- ✅ Streaming response support
- ✅ Configurable generation parameters

### **2. RAG Chat Flow**
- ✅ **Input**: question + doc_id (optional)
- ✅ **Search**: Tìm kiếm context từ FAISS
- ✅ **Generate**: Tạo câu trả lời với LLM
- ✅ **Response**: Trả về answer + sources

### **3. API Endpoints**
- ✅ `POST /api/chat` - Chat cơ bản
- ✅ `POST /api/chat/document/{doc_id}` - Chat với document cụ thể
- ✅ `POST /api/chat/stream` - Streaming chat
- ✅ `GET /api/chat/stats` - Thống kê hệ thống

## 🚀 **CÀI ĐẶT MODEL**

### **1. Tải model gpt-oss-20b**

```bash
# Tạo thư mục
mkdir -p models/llm

# Tải model (cần có internet lần đầu)
python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
model_name = 'gpt-oss-20b'  # Hoặc đường dẫn model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer.save_pretrained('models/llm')
model.save_pretrained('models/llm')
print('Model downloaded successfully!')
"
```

### **2. Kiểm tra model**

```bash
# Kiểm tra thư mục model
ls -la models/llm/
# Nên có các file: config.json, pytorch_model.bin, tokenizer.json, etc.
```

## 📚 **API ENDPOINTS**

### **1. Basic Chat**
```http
POST /api/chat
Content-Type: application/json

{
    "question": "Trí tuệ nhân tạo là gì?",
    "top_k": 5,
    "max_tokens": 1000,
    "temperature": 0.7
}
```

**Response:**
```json
{
    "response": "Trí tuệ nhân tạo (AI) là một lĩnh vực...",
    "sources": [
        {
            "content": "Trí tuệ nhân tạo là...",
            "similarity_score": 0.95,
            "document_id": "doc_uuid",
            "filename": "document.txt",
            "chunk_index": 1
        }
    ],
    "processing_time": 2.5,
    "question": "Trí tuệ nhân tạo là gì?",
    "doc_id": null
}
```

### **2. Document Chat**
```http
POST /api/chat/document/{document_id}
Content-Type: application/json

{
    "question": "Hãy tóm tắt nội dung chính",
    "top_k": 3
}
```

### **3. Streaming Chat**
```http
POST /api/chat/stream
Content-Type: application/json

{
    "question": "Giải thích về machine learning",
    "top_k": 5
}
```

**Response (Server-Sent Events):**
```
data: {"type": "start", "question": "Giải thích về machine learning", "sources_count": 3}

data: {"type": "token", "content": "Machine"}

data: {"type": "token", "content": " learning"}

data: {"type": "token", "content": " là"}

data: {"type": "end"}
```

### **4. Chat Stats**
```http
GET /api/chat/stats
```

**Response:**
```json
{
    "llm_service": {
        "model_loaded": true,
        "model_path": "models/llm",
        "device": "cuda",
        "model_name": "gpt-oss-20b"
    },
    "embedding_service": {
        "model_loaded": true,
        "model_path": "models/embedding"
    },
    "faiss_store": {
        "total_vectors": 150,
        "documents_count": 5
    },
    "chat_capabilities": {
        "text_chat": true,
        "document_chat": true,
        "streaming_chat": true,
        "rag_enabled": true
    }
}
```

## 🔧 **SỬ DỤNG TRONG CODE**

### **1. Basic Chat**
```python
from services.llm_service import llm_service

# Tạo câu trả lời với context
question = "Trí tuệ nhân tạo là gì?"
context = "Trí tuệ nhân tạo là lĩnh vực khoa học máy tính..."

answer = llm_service.generate_answer(question, context)
print(answer)
```

### **2. Chat với RAG**
```python
from services.embedding_service import embedding_service
from services.llm_service import llm_service
from db.faiss_store import faiss_store

# Search context
search_results = faiss_store.search_text(
    query_text="machine learning",
    top_k=3,
    embedding_service=embedding_service
)

# Create context
context = "\n".join([r["content"] for r in search_results])

# Generate answer
answer = llm_service.generate_answer("Machine learning là gì?", context)
print(answer)
```

### **3. Streaming Response**
```python
# Stream response tokens
for token in llm_service.generate_answer_with_streaming(question, context):
    print(token, end="", flush=True)
```

## 🚀 **CÁCH SỬ DỤNG**

### **1. Test Chatbot**
```bash
# Chạy test script
python test_chat.py
```

### **2. API Testing**
```bash
# Basic chat
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "Trí tuệ nhân tạo là gì?", "top_k": 5}'

# Document chat
curl -X POST "http://localhost:8000/api/chat/document/document_uuid" \
  -H "Content-Type: application/json" \
  -d '{"question": "Tóm tắt nội dung chính"}'

# Chat stats
curl "http://localhost:8000/api/chat/stats"
```

### **3. Workflow hoàn chỉnh**
```bash
# 1. Upload document
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.txt"

# 2. Create embeddings
curl -X POST "http://localhost:8000/api/embed/document/{doc_id}" \
  -H "Content-Type: application/json" \
  -d '{"chunk_size": 500, "chunk_overlap": 50}'

# 3. Chat with document
curl -X POST "http://localhost:8000/api/chat/document/{doc_id}" \
  -H "Content-Type: application/json" \
  -d '{"question": "Nội dung chính của tài liệu là gì?"}'
```

## 📊 **RAG FLOW**

### **1. Input Processing**
```
User Question → Validation → Text Cleaning
```

### **2. Context Retrieval**
```
Question → Embedding → FAISS Search → Top-K Chunks
```

### **3. Context Formatting**
```
Chunks → Context Creation → Prompt Building
```

### **4. LLM Generation**
```
Prompt → LLM → Response → Post-processing
```

### **5. Response Formatting**
```
Response + Sources → JSON Response
```

## ⚡ **PERFORMANCE**

### **Benchmarks**
- **Basic Chat**: ~2-5s (bao gồm LLM generation)
- **RAG Chat**: ~3-8s (bao gồm search + generation)
- **Streaming Chat**: ~1-3s (first token)
- **Document Chat**: ~2-6s (với document filter)

### **Tối ưu hóa**
- ✅ **Model Caching**: Load model một lần
- ✅ **Batch Processing**: Xử lý multiple requests
- ✅ **Context Optimization**: Chỉ lấy top-k chunks
- ✅ **Memory Management**: GPU memory cleanup

## 🔍 **CẤU HÌNH**

### **Generation Parameters**
```python
# Cập nhật generation config
llm_service.update_generation_config(
    max_new_tokens=1500,
    temperature=0.8,
    top_p=0.95,
    top_k=50
)
```

### **Search Parameters**
```python
# Cấu hình search
search_params = {
    "top_k": 5,        # Số chunks
    "doc_id": None,    # Document filter
    "temperature": 0.7 # LLM temperature
}
```

## 🐛 **TROUBLESHOOTING**

### **1. Model không load được**
```bash
# Kiểm tra thư mục model
ls -la models/llm/

# Kiểm tra logs
tail -f logs/app.log
```

### **2. Chat response chậm**
```bash
# Kiểm tra GPU usage
nvidia-smi

# Kiểm tra memory
htop
```

### **3. Không tìm thấy context**
```bash
# Kiểm tra FAISS index
curl "http://localhost:8000/api/embed/stats"

# Kiểm tra documents
curl "http://localhost:8000/api/documents"
```

## 📝 **NOTES**

- **Model**: gpt-oss-20b (20B parameters)
- **Context Length**: 2048 tokens
- **Generation**: Configurable parameters
- **RAG**: Tích hợp với FAISS search
- **Streaming**: Server-Sent Events
- **Offline**: Hoàn toàn offline, không cần internet
- **Memory**: Cần ít nhất 16GB RAM cho model 20B
- **GPU**: Khuyến nghị GPU với ít nhất 12GB VRAM
