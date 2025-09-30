# Hướng Dẫn Triển Khai Hệ Thống Chatbot RAG + LLM Offline

Hướng dẫn chi tiết triển khai hệ thống chatbot RAG + LLM hoàn toàn offline trên Ubuntu.

## 📋 **MỤC LỤC**

1. [Chuẩn bị môi trường](#1-chuẩn-bị-môi-trường)
2. [Chuẩn bị model offline](#2-chuẩn-bị-model-offline)
3. [Chạy backend FastAPI](#3-chạy-backend-fastapi)
4. [Build frontend ReactJS](#4-build-frontend-reactjs)
5. [Kết nối frontend ↔ backend](#5-kết-nối-frontend--backend)
6. [Chạy toàn hệ thống qua Docker Compose](#6-chạy-toàn-hệ-thống-qua-docker-compose)
7. [Kiểm thử trong môi trường không có internet](#7-kiểm-thử-trong-môi-trường-không-có-internet)

---

## 1. **CHUẨN BỊ MÔI TRƯỜNG**

### **1.1. Cài đặt Python 3.9+**

```bash
# Cập nhật package list
sudo apt update

# Cài đặt Python 3.9 và pip
sudo apt install -y python3.9 python3.9-pip python3.9-venv python3.9-dev

# Tạo symbolic link
sudo ln -sf /usr/bin/python3.9 /usr/bin/python3
sudo ln -sf /usr/bin/python3.9 /usr/bin/python

# Kiểm tra version
python3 --version
pip3 --version
```

### **1.2. Cài đặt NodeJS 18+**

```bash
# Cài đặt NodeJS 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Kiểm tra version
node --version
npm --version
```

### **1.3. Cài đặt Docker và Docker Compose**

```bash
# Cài đặt Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Thêm user vào docker group
sudo usermod -aG docker $USER

# Cài đặt Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Kiểm tra installation
docker --version
docker-compose --version

# Logout và login lại để áp dụng group changes
```

### **1.4. Cài đặt CUDA (Nếu có GPU)**

```bash
# Kiểm tra GPU
lspci | grep -i nvidia

# Cài đặt CUDA Toolkit 11.8
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda

# Thêm CUDA vào PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Kiểm tra CUDA
nvcc --version
nvidia-smi
```

### **1.5. Cài đặt Dependencies**

```bash
# Tạo virtual environment
cd /path/to/your/project
python3 -m venv venv
source venv/bin/activate

# Cài đặt Python dependencies
pip install --upgrade pip
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install pydantic==2.5.0
pip install python-multipart==0.0.6
pip install sentence-transformers==2.2.2
pip install transformers==4.35.0
pip install torch==2.1.0
pip install faiss-cpu==1.7.4
pip install numpy==1.24.3
pip install PyPDF2==3.0.1
pip install python-docx==1.1.0
pip install aiofiles==23.2.1
pip install python-dotenv==1.0.0
pip install pydantic-settings==2.0.3

# Cài đặt thêm cho GPU (nếu có)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install faiss-gpu==1.7.4
pip install accelerate
pip install bitsandbytes

# Cài đặt NodeJS dependencies
cd frontend
npm install
cd ..
```

---

## 2. **CHUẨN BỊ MODEL OFFLINE**

### **2.1. Tạo cấu trúc thư mục**

```bash
# Tạo thư mục cho models
mkdir -p models/embedding
mkdir -p models/llm
mkdir -p data/docs
mkdir -p data/faiss_index
mkdir -p data/metadata
mkdir -p uploads
```

### **2.2. Tải Embedding Model (intfloat/multilingual-e5-large)**

```bash
# Tạo script tải embedding model
cat > download_embedding.py << 'EOF'
import os
from sentence_transformers import SentenceTransformer
import torch

print("📥 Downloading multilingual-e5-large...")
print("This may take a while depending on your internet connection...")

try:
    # Tải model
    model = SentenceTransformer('intfloat/multilingual-e5-large')
    
    # Lưu model vào thư mục local
    model.save('models/embedding')
    
    print("✅ Embedding model downloaded and saved successfully!")
    print(f"Model saved to: {os.path.abspath('models/embedding')}")
    
    # Test model
    print("🧪 Testing model...")
    test_text = "This is a test sentence for embedding"
    embedding = model.encode(test_text)
    print(f"✅ Test embedding generated: shape {embedding.shape}")
    
except Exception as e:
    print(f"❌ Error downloading model: {e}")
EOF

# Chạy script tải model
python download_embedding.py
```

### **2.3. Tải LLM Model (gpt-oss-20b)**

```bash
# Tạo script tải LLM model
cat > download_llm.py << 'EOF'
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

print("📥 Downloading gpt-oss-20b...")
print("This may take a while depending on your internet connection...")
print("Model size: ~40GB")

try:
    model_name = "gpt-oss-20b"  # Hoặc đường dẫn model cụ thể
    
    # Tải tokenizer
    print("Downloading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Tải model
    print("Downloading model (this will take a long time)...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        low_cpu_mem_usage=True
    )
    
    # Lưu model và tokenizer
    print("Saving model and tokenizer...")
    tokenizer.save_pretrained('models/llm')
    model.save_pretrained('models/llm')
    
    print("✅ LLM model downloaded and saved successfully!")
    print(f"Model saved to: {os.path.abspath('models/llm')}")
    
    # Test model
    print("🧪 Testing model...")
    test_prompt = "Hello, how are you?"
    inputs = tokenizer(test_prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            temperature=0.7,
            do_sample=True
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"✅ Test generation successful!")
    print(f"Input: {test_prompt}")
    print(f"Output: {response}")
    
except Exception as e:
    print(f"❌ Error downloading model: {e}")
    print("Please check your internet connection and try again.")
EOF

# Chạy script tải model
python download_llm.py
```

### **2.4. Kiểm tra models đã tải**

```bash
# Kiểm tra embedding model
ls -la models/embedding/
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('models/embedding', local_files_only=True)
print('✅ Embedding model loaded successfully')
"

# Kiểm tra LLM model
ls -la models/llm/
python -c "
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained('models/llm', local_files_only=True)
print('✅ LLM model loaded successfully')
"
```

---

## 3. **CHẠY BACKEND FASTAPI**

### **3.1. Cấu hình Backend**

```bash
# Tạo file .env cho backend
cat > backend/.env << 'EOF'
# Backend Configuration
APP_NAME=RAG + LLM Chatbot API
APP_VERSION=1.0.0
DEBUG=True

# Paths
DATA_DIR=data
DOCS_DIR=data/docs
FAISS_INDEX_DIR=data/faiss_index
FAISS_STORE_DIR=data/faiss_store
METADATA_DIR=data/metadata
UPLOADS_DIR=uploads

# Model paths
MODELS_DIR=models
EMBEDDING_MODEL_PATH=models/embedding
LLM_MODEL_PATH=models/llm

# Embedding settings
EMBEDDING_CHUNK_SIZE=500
EMBEDDING_CHUNK_OVERLAP=50

# LLM settings
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.7
LLM_TOP_K=5

# Document metadata file
DOCUMENTS_METADATA_FILE=data/metadata/documents_metadata.json
FAISS_METADATA_FILE=data/metadata/faiss_metadata.json

# Model cache directory
MODEL_CACHE_DIR=models/cache
EOF
```

### **3.2. Chạy Backend**

```bash
# Di chuyển vào thư mục backend
cd backend

# Kích hoạt virtual environment
source ../venv/bin/activate

# Chạy backend
python main.py

# Hoặc sử dụng uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **3.3. Kiểm tra Backend**

```bash
# Test health check
curl http://localhost:8000/api/health

# Test API documentation
# Mở browser: http://localhost:8000/docs
```

---

## 4. **BUILD FRONTEND REACTJS**

### **4.1. Cấu hình Frontend**

```bash
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt dependencies
npm install

# Tạo file .env cho frontend
cat > .env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=RAG Chatbot
VITE_APP_VERSION=1.0.0
EOF
```

### **4.2. Build Frontend**

```bash
# Build cho production
npm run build

# Hoặc chạy development server
npm run dev
```

### **4.3. Kiểm tra Frontend**

```bash
# Test development server
# Mở browser: http://localhost:5173

# Test production build
npx serve -s dist -l 3000
# Mở browser: http://localhost:3000
```

---

## 5. **KẾT NỐI FRONTEND ↔ BACKEND**

### **5.1. Cấu hình CORS**

```bash
# Kiểm tra CORS trong backend/main.py
# Đảm bảo có:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **5.2. Test kết nối**

```bash
# Test API từ frontend
curl -X GET http://localhost:8000/api/health

# Test upload document
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test_document.txt"

# Test chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello, how are you?", "top_k": 5}'
```

### **5.3. Kiểm tra Frontend-Backend Integration**

```bash
# Mở browser và test:
# 1. Upload document
# 2. Generate embeddings
# 3. Chat với document
# 4. Test streaming response
```

---

## 6. **CHẠY TOÀN HỆ THỐNG QUA DOCKER COMPOSE**

### **6.1. Tạo Dockerfile cho Backend**

```bash
cat > backend/Dockerfile << 'EOF'
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/docs data/faiss_index data/metadata uploads models/embedding models/llm

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

### **6.2. Tạo Dockerfile cho Frontend**

```bash
cat > frontend/Dockerfile << 'EOF'
# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
EOF
```

### **6.3. Tạo nginx.conf cho Frontend**

```bash
cat > frontend/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;
        server_name localhost;

        root /usr/share/nginx/html;
        index index.html;

        # Handle client-side routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Proxy API requests to backend
        location /api/ {
            proxy_pass http://backend:8000/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF
```

### **6.4. Tạo docker-compose.yml**

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: rag-chatbot-backend
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
      - ./uploads:/app/uploads
    environment:
      - PYTHONPATH=/app
      - DEBUG=True
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    container_name: rag-chatbot-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  models:
    driver: local
  data:
    driver: local
EOF
```

### **6.5. Chạy Docker Compose**

```bash
# Build và chạy containers
docker-compose up --build -d

# Kiểm tra status
docker-compose ps

# Xem logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### **6.6. Kiểm tra Docker Deployment**

```bash
# Test backend
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:80

# Mở browser: http://localhost
```

---

## 7. **KIỂM THỬ TRONG MÔI TRƯỜNG KHÔNG CÓ INTERNET**

### **7.1. Chuẩn bị môi trường offline**

```bash
# Tắt internet connection
sudo ifconfig eth0 down
# Hoặc
sudo systemctl stop NetworkManager

# Kiểm tra không có internet
ping google.com
# Should fail
```

### **7.2. Test Backend Offline**

```bash
# Chạy backend
cd backend
source ../venv/bin/activate
python main.py

# Test health check
curl http://localhost:8000/api/health

# Test model loading
curl http://localhost:8000/api/chat/stats
```

### **7.3. Test Frontend Offline**

```bash
# Chạy frontend
cd frontend
npm run dev

# Mở browser: http://localhost:5173
# Test upload document
# Test chat functionality
```

### **7.4. Test Docker Offline**

```bash
# Chạy Docker Compose
docker-compose up -d

# Test services
curl http://localhost:8000/api/health
curl http://localhost:80

# Mở browser: http://localhost
```

### **7.5. Test toàn bộ workflow offline**

```bash
# 1. Upload document
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test_document.txt"

# 2. Generate embeddings
curl -X POST http://localhost:8000/api/embed/document/{doc_id}

# 3. Test chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "top_k": 5}'

# 4. Test streaming chat
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain the main points", "top_k": 3}'
```

### **7.6. Performance testing offline**

```bash
# Test response time
time curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question", "top_k": 5}'

# Test memory usage
docker stats

# Test concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"question": "Test question ' $i '", "top_k": 5}' &
done
wait
```

---

## 🎯 **KIỂM TRA CUỐI CÙNG**

### **Checklist triển khai**

- [ ] Python 3.9+ đã cài đặt
- [ ] NodeJS 18+ đã cài đặt
- [ ] Docker và Docker Compose đã cài đặt
- [ ] CUDA đã cài đặt (nếu có GPU)
- [ ] Embedding model đã tải về `models/embedding/`
- [ ] LLM model đã tải về `models/llm/`
- [ ] Backend chạy được trên port 8000
- [ ] Frontend build và chạy được
- [ ] Frontend kết nối được với backend
- [ ] Docker Compose chạy được
- [ ] Hệ thống hoạt động offline hoàn toàn

### **Test cuối cùng**

```bash
# 1. Test toàn bộ hệ thống
curl http://localhost:8000/api/health
curl http://localhost:80

# 2. Test upload và chat
# Mở browser: http://localhost
# Upload document → Generate embeddings → Chat

# 3. Test offline
# Tắt internet → Test lại toàn bộ workflow

# 4. Test performance
# Test với nhiều documents và queries
```

---

## 🚀 **KẾT LUẬN**

Hệ thống chatbot RAG + LLM offline đã được triển khai thành công với:

- ✅ **Hoàn toàn offline**: Không cần internet khi chạy
- ✅ **GPU optimized**: Sử dụng CUDA cho performance tốt
- ✅ **Docker ready**: Triển khai dễ dàng với Docker Compose
- ✅ **Production ready**: Error handling và monitoring
- ✅ **Scalable**: Có thể mở rộng theo nhu cầu

Hệ thống sẵn sàng cho production với khả năng hoạt động hoàn toàn offline!
