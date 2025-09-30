"""
Setup script để tải models
Script tải các AI models cần thiết cho hệ thống
"""

import os
import sys
from pathlib import Path
import subprocess

def download_embedding_model():
    """Tải embedding model"""
    print("📥 Downloading embedding model (intfloat/multilingual-e5-large)...")
    
    model_path = Path("models/embedding")
    model_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Tải model bằng sentence-transformers
        script = """
from sentence_transformers import SentenceTransformer
import os

print("Downloading multilingual-e5-large...")
model = SentenceTransformer('intfloat/multilingual-e5-large')
model.save('models/embedding')
print("✅ Embedding model downloaded successfully!")
"""
        
        with open("temp_download_embedding.py", "w") as f:
            f.write(script)
        
        subprocess.run([sys.executable, "temp_download_embedding.py"], check=True)
        os.remove("temp_download_embedding.py")
        
        print("✅ Embedding model ready!")
        
    except Exception as e:
        print(f"❌ Error downloading embedding model: {e}")
        print("Please download manually:")
        print("1. Go to https://huggingface.co/intfloat/multilingual-e5-large")
        print("2. Download all files to models/embedding/")

def download_llm_model():
    """Tải LLM model"""
    print("📥 Downloading LLM model (gpt-oss-20b)...")
    
    model_path = Path("models/llm")
    model_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Tải model bằng transformers
        script = """
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

print("Downloading gpt-oss-20b...")
model_name = "gpt-oss-20b"  # Hoặc đường dẫn model cụ thể

try:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    tokenizer.save_pretrained('models/llm')
    model.save_pretrained('models/llm')
    print("✅ LLM model downloaded successfully!")
except Exception as e:
    print(f"Error: {e}")
    print("Please check model name or download manually")
"""
        
        with open("temp_download_llm.py", "w") as f:
            f.write(script)
        
        subprocess.run([sys.executable, "temp_download_llm.py"], check=True)
        os.remove("temp_download_llm.py")
        
        print("✅ LLM model ready!")
        
    except Exception as e:
        print(f"❌ Error downloading LLM model: {e}")
        print("Please download manually:")
        print("1. Go to https://huggingface.co/gpt-oss-20b")
        print("2. Download all files to models/llm/")

def check_models():
    """Kiểm tra models đã tải"""
    embedding_path = Path("models/embedding")
    llm_path = Path("models/llm")
    
    print("\n🔍 Checking downloaded models...")
    
    if embedding_path.exists() and any(embedding_path.iterdir()):
        print("✅ Embedding model found")
        files = list(embedding_path.glob("*"))
        print(f"   Files: {len(files)}")
    else:
        print("❌ Embedding model not found")
    
    if llm_path.exists() and any(llm_path.iterdir()):
        print("✅ LLM model found")
        files = list(llm_path.glob("*"))
        print(f"   Files: {len(files)}")
    else:
        print("❌ LLM model not found")

def main():
    """Main setup function"""
    print("🤖 RAG + LLM Chatbot Model Setup")
    print("=" * 50)
    
    # Tạo thư mục models
    Path("models").mkdir(exist_ok=True)
    
    # Tải embedding model
    download_embedding_model()
    
    # Tải LLM model
    download_llm_model()
    
    # Kiểm tra models
    check_models()
    
    print("\n" + "=" * 50)
    print("✅ Model setup completed!")
    print("You can now run: python start.py")

if __name__ == "__main__":
    main()
