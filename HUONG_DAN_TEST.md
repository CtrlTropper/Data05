# HƯỚNG DẪN TEST HỆ THỐNG RAG + LLM CHATBOT

## Tổng quan hệ thống

Hệ thống RAG + LLM Chatbot là một ứng dụng chatbot chuyên về An toàn Thông tin (ATTT) với các tính năng chính:
- **RAG (Retrieval-Augmented Generation)**: Tìm kiếm thông tin từ tài liệu và tạo câu trả lời
- **LLM Offline**: Sử dụng mô hình gpt-oss-20b chạy offline
- **Embedding**: Sử dụng multilingual-e5-large để tạo vector embeddings
- **FAISS**: Lưu trữ và tìm kiếm vector
- **Security Filter**: Lọc câu hỏi chỉ liên quan đến ATTT
- **Chat Sessions**: Quản lý lịch sử hội thoại
- **PDF OCR**: Xử lý PDF với OCR cho tiếng Việt và tiếng Anh

## Thứ tự test được khuyến nghị

### Bước 1: Chuẩn bị môi trường

#### 1.1. Kiểm tra môi trường
```bash
# Kích hoạt môi trường ảo (nếu sử dụng conda)
conda activate vian

# Kiểm tra Python version (cần >= 3.8)
python --version

# Cài đặt dependencies
cd backend
pip install -r requirements.txt
```

#### 1.2. Tạo thư mục cần thiết
```bash
# Tạo các thư mục cần thiết
mkdir -p data/faiss_index
mkdir -p data/faiss_store
mkdir -p data/metadata
mkdir -p data/docs
mkdir -p uploads
mkdir -p models/embedding
mkdir -p models/llm
mkdir -p logs
```

#### 1.3. Kiểm tra models
```bash
# Kiểm tra embedding model
ls models/embedding/
# Cần có: intfloat/multilingual-e5-large

# Kiểm tra LLM model  
ls models/llm/
# Cần có: gpt-oss-20b
```

### Bước 2: Test các service cơ bản (Không cần backend chạy)

#### 2.1. Test Security Filter
```bash
cd backend
python test_security_filter.py
```
**Mục đích**: Kiểm tra bộ lọc câu hỏi ATTT
**Kết quả mong đợi**: 
- ✅ Các câu hỏi về ATTT được chấp nhận
- ❌ Các câu hỏi không liên quan bị từ chối

#### 2.2. Test PDF OCR
```bash
python test_pdf_ocr.py
```
**Mục đích**: Kiểm tra khả năng xử lý PDF với OCR
**Kết quả mong đợi**:
- ✅ PDF processor khởi tạo thành công
- ✅ OCR languages (vie, eng) có sẵn
- ⚠️ Cần file PDF test để test đầy đủ

#### 2.3. Test LLM Service
```bash
python test_llm_service.py
```
**Mục đích**: Kiểm tra mô hình LLM offline
**Kết quả mong đợi**:
- ✅ Model gpt-oss-20b load thành công
- ✅ Tạo câu trả lời cơ bản
- ✅ Streaming response hoạt động
- ✅ GPU memory management

#### 2.4. Test Vector Integration
```bash
python test_vector_integration.py
```
**Mục đích**: Kiểm tra embedding + FAISS
**Kết quả mong đợi**:
- ✅ Embedding model load thành công
- ✅ Tạo embeddings cho text
- ✅ FAISS index hoạt động
- ✅ Search vector hoạt động

### Bước 3: Test Search System
```bash
python test_search.py
```
**Mục đích**: Kiểm tra hệ thống tìm kiếm
**Kết quả mong đợi**:
- ✅ Embedding service hoạt động
- ✅ FAISS store hoạt động
- ✅ Text search trả về kết quả
- ✅ Vector search hoạt động
- ✅ Document filter hoạt động

### Bước 4: Khởi động Backend

#### 4.1. Khởi động server
```bash
# Cách 1: Sử dụng start.py (khuyến nghị)
python start.py

# Cách 2: Sử dụng main.py trực tiếp
python main.py

# Cách 3: Sử dụng uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4.2. Kiểm tra server
```bash
# Kiểm tra health endpoint
curl http://localhost:8000/api/health

# Kiểm tra API docs
# Mở browser: http://localhost:8000/docs
```

### Bước 5: Test API Endpoints (Backend đang chạy)

#### 5.1. Test Chat System
```bash
python test_chat.py
```
**Mục đích**: Kiểm tra API chat
**Kết quả mong đợi**:
- ✅ Health check thành công
- ✅ Chat stats hiển thị đúng
- ✅ Basic chat hoạt động
- ✅ Document chat hoạt động (nếu có tài liệu)
- ✅ Search functionality hoạt động
- ✅ Embedding functionality hoạt động
- ✅ Performance test đạt yêu cầu

#### 5.2. Test Security Chat
```bash
python test_security_chat.py
```
**Mục đích**: Kiểm tra chatbot chỉ trả lời câu hỏi ATTT
**Kết quả mong đợi**:
- ✅ Câu hỏi ATTT được xử lý
- ❌ Câu hỏi không liên quan bị từ chối
- ✅ Streaming chat hoạt động
- ✅ Security domain classification

#### 5.3. Test Vietnamese Translation
```bash
python test_vietnamese_translation.py
```
**Mục đích**: Kiểm tra dịch tiếng Anh sang tiếng Việt
**Kết quả mong đợi**:
- ✅ Câu hỏi tiếng Việt giữ nguyên
- ✅ Câu hỏi tiếng Anh được dịch sang tiếng Việt
- ✅ Streaming translation hoạt động
- ✅ Language detection chính xác

### Bước 6: Test Chat Sessions & Memory

#### 6.1. Test Chat Sessions
```bash
python test_chat_sessions.py
```
**Mục đích**: Kiểm tra quản lý chat sessions
**Kết quả mong đợi**:
- ✅ Tạo session thành công
- ✅ Liệt kê sessions
- ✅ Lấy thông tin session
- ✅ Thêm tin nhắn vào session
- ✅ Chat với session
- ✅ Streaming chat với session
- ✅ Xóa session

#### 6.2. Test Conversation Memory
```bash
python test_conversation_memory.py
```
**Mục đích**: Kiểm tra trí nhớ hội thoại
**Kết quả mong đợi**:
- ✅ Chatbot nhớ context giữa các câu hỏi
- ✅ Chat không session không có trí nhớ
- ✅ Memory limit hoạt động
- ✅ Streaming chat với memory

### Bước 7: Test Full System Integration
```bash
python test_full_system.py
```
**Mục đích**: Kiểm tra tích hợp toàn bộ hệ thống
**Kết quả mong đợi**:
- ✅ Health check
- ✅ System stats
- ✅ Document management
- ✅ Embedding system
- ✅ Search system
- ✅ Chat system
- ✅ Document chat
- ✅ Performance test

## Xử lý lỗi thường gặp

### Lỗi Model không tìm thấy
```
❌ Model not found in models/embedding/
❌ Model not found in models/llm/
```
**Giải pháp**:
1. Tải model embedding: `intfloat/multilingual-e5-large`
2. Tải model LLM: `gpt-oss-20b`
3. Đặt vào đúng thư mục `models/embedding/` và `models/llm/`

### Lỗi GPU Memory
```
❌ CUDA out of memory
```
**Giải pháp**:
1. Giảm batch size
2. Sử dụng CPU thay vì GPU
3. Clear GPU cache: `llm_service.clear_gpu_cache()`

### Lỗi FAISS Index
```
❌ FAISS index not found
```
**Giải pháp**:
1. Tạo lại FAISS index
2. Kiểm tra quyền ghi thư mục `data/faiss_index/`
3. Chạy lại embedding process

### Lỗi OCR
```
❌ Tesseract not found
```
**Giải pháp**:
1. Cài đặt Tesseract OCR
2. Cài đặt language packs (vie, eng)
3. Cập nhật PATH environment

### Lỗi Backend không khởi động
```
❌ Backend is not running
```
**Giải pháp**:
1. Kiểm tra port 8000 có bị chiếm không
2. Kiểm tra dependencies đã cài đặt
3. Kiểm tra logs để xem lỗi chi tiết
4. Thử khởi động với `python start.py`

## Checklist Test

### ✅ Test Cơ bản (Không cần backend)
- [ ] Security Filter
- [ ] PDF OCR
- [ ] LLM Service
- [ ] Vector Integration
- [ ] Search System

### ✅ Test API (Cần backend chạy)
- [ ] Chat System
- [ ] Security Chat
- [ ] Vietnamese Translation
- [ ] Chat Sessions
- [ ] Conversation Memory
- [ ] Full System Integration

### ✅ Test Performance
- [ ] Response time < 5s cho câu hỏi đơn giản
- [ ] Response time < 10s cho câu hỏi phức tạp
- [ ] Memory usage ổn định
- [ ] GPU memory không bị leak

### ✅ Test Security
- [ ] Chỉ trả lời câu hỏi ATTT
- [ ] Từ chối câu hỏi không liên quan
- [ ] Không tiết lộ thông tin nhạy cảm
- [ ] Input validation hoạt động

## Lưu ý quan trọng

1. **Thứ tự test**: Luôn test theo thứ tự từ cơ bản đến phức tạp
2. **Môi trường**: Đảm bảo môi trường ảo được kích hoạt
3. **Models**: Cần tải đầy đủ models trước khi test
4. **Backend**: Một số test cần backend chạy, một số không
5. **Dependencies**: Cài đặt đầy đủ requirements.txt
6. **GPU**: Nếu có GPU, đảm bảo CUDA được cài đặt
7. **OCR**: Cần cài đặt Tesseract OCR cho chức năng PDF
8. **Logs**: Kiểm tra logs khi có lỗi để debug

## Kết luận

Hệ thống RAG + LLM Chatbot được thiết kế để hoạt động offline hoàn toàn với khả năng xử lý câu hỏi về An toàn Thông tin bằng tiếng Việt. Việc test theo thứ tự này sẽ giúp phát hiện và khắc phục lỗi một cách có hệ thống, đảm bảo hệ thống hoạt động ổn định trước khi triển khai production.
