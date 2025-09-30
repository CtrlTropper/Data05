#!/bin/bash

# RAG + LLM Chatbot System Startup Script
# Script khởi chạy hệ thống chatbot

echo "🚀 RAG + LLM Chatbot System"
echo "=========================="

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✅ Python: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p data/{faiss_index,faiss_store,metadata,docs}
mkdir -p uploads
mkdir -p models/{embedding,llm}
mkdir -p logs

# Check models
echo "🤖 Checking models..."
if [ ! -d "models/embedding" ] || [ -z "$(ls -A models/embedding)" ]; then
    echo "⚠️  Embedding model not found"
    echo "   Run: python setup_models.py"
fi

if [ ! -d "models/llm" ] || [ -z "$(ls -A models/llm)" ]; then
    echo "⚠️  LLM model not found"
    echo "   Run: python setup_models.py"
fi

# Start server
echo "🚀 Starting FastAPI server..."
echo "   Access API docs at: http://localhost:8000/docs"
echo "   Press Ctrl+C to stop"
echo "=========================="

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
