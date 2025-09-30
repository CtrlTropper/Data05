"""
Startup script cho RAG + LLM Chatbot System
Script khởi chạy hệ thống với kiểm tra dependencies
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Kiểm tra phiên bản Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_dependencies():
    """Kiểm tra dependencies"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "sentence-transformers",
        "transformers",
        "torch",
        "faiss-cpu",
        "numpy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} not found")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            sys.exit(1)

def create_directories():
    """Tạo các thư mục cần thiết"""
    directories = [
        "data/faiss_index",
        "data/faiss_store", 
        "data/metadata",
        "data/docs",
        "uploads",
        "models/embedding",
        "models/llm",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory created: {directory}")

def check_models():
    """Kiểm tra models"""
    embedding_path = Path("models/embedding")
    llm_path = Path("models/llm")
    
    if not embedding_path.exists() or not any(embedding_path.iterdir()):
        print("⚠️  Embedding model not found in models/embedding/")
        print("   Please download intfloat/multilingual-e5-large to models/embedding/")
    else:
        print("✅ Embedding model found")
    
    if not llm_path.exists() or not any(llm_path.iterdir()):
        print("⚠️  LLM model not found in models/llm/")
        print("   Please download gpt-oss-20b to models/llm/")
    else:
        print("✅ LLM model found")

def main():
    """Main startup function"""
    print("🚀 RAG + LLM Chatbot System Startup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    check_dependencies()
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Check models
    print("\n🤖 Checking models...")
    check_models()
    
    print("\n" + "=" * 50)
    print("✅ System ready to start!")
    print("\n🚀 Starting FastAPI server...")
    print("   Access API docs at: http://localhost:8000/docs")
    print("   Press Ctrl+C to stop")
    print("=" * 50)
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
