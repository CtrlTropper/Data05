#!/bin/bash

# Setup script for RAG + LLM Chatbot System
# Hướng dẫn cài đặt môi trường cho hệ thống chatbot RAG + LLM offline

set -e  # Exit on any error

echo "🚀 Setting up RAG + LLM Chatbot System Environment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Update package list
print_header "Updating package list..."
sudo apt update

# Install Python 3.9+
print_header "Installing Python 3.9+..."
sudo apt install -y python3.9 python3.9-pip python3.9-venv python3.9-dev
sudo ln -sf /usr/bin/python3.9 /usr/bin/python3
sudo ln -sf /usr/bin/python3.9 /usr/bin/python

# Verify Python installation
python3 --version
pip3 --version

# Install NodeJS 18+
print_header "Installing NodeJS 18+..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify NodeJS installation
node --version
npm --version

# Install Docker
print_header "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
print_header "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify Docker installation
docker --version
docker-compose --version

# Check for NVIDIA GPU
print_header "Checking for NVIDIA GPU..."
if command -v nvidia-smi &> /dev/null; then
    print_status "NVIDIA GPU detected"
    nvidia-smi
else
    print_warning "No NVIDIA GPU detected. CUDA installation skipped."
    print_warning "For GPU support, install CUDA manually."
fi

# Create project directories
print_header "Creating project directories..."
mkdir -p models/embedding
mkdir -p models/llm
mkdir -p data/docs
mkdir -p data/faiss_index
mkdir -p data/metadata
mkdir -p uploads

# Create virtual environment
print_header "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_header "Installing Python dependencies..."
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

# Install GPU dependencies if CUDA is available
if command -v nvidia-smi &> /dev/null; then
    print_header "Installing GPU dependencies..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    pip install faiss-gpu==1.7.4
    pip install accelerate
    pip install bitsandbytes
fi

# Install NodeJS dependencies
print_header "Installing NodeJS dependencies..."
cd frontend
npm install
cd ..

# Create environment files
print_header "Creating environment files..."

# Backend .env
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

# Frontend .env
cat > frontend/.env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=RAG Chatbot
VITE_APP_VERSION=1.0.0
EOF

# Make scripts executable
chmod +x backend/run.sh
chmod +x setup_embedding_model.py
chmod +x setup_llm_model.py

print_status "Environment setup completed successfully!"
print_warning "Please logout and login again to apply Docker group changes."
print_warning "Then run the following commands to download models:"
echo ""
echo "1. Download embedding model:"
echo "   python setup_embedding_model.py"
echo ""
echo "2. Download LLM model:"
echo "   python setup_llm_model.py"
echo ""
echo "3. Test the system:"
echo "   python test_vector_integration.py"
echo "   python test_llm_service.py"
echo ""
echo "4. Run with Docker:"
echo "   docker-compose up --build -d"
echo ""
print_status "Setup complete! 🎉"
