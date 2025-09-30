"""
Setup script để tải embedding model offline
Script tải intfloat/multilingual-e5-large về local
"""

import os
import sys
import subprocess
from pathlib import Path

def download_embedding_model():
    """Tải embedding model intfloat/multilingual-e5-large"""
    print("📥 Downloading embedding model (intfloat/multilingual-e5-large)...")
    
    model_path = Path("models/embedding")
    model_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Script để tải model
        script = """
import os
from sentence_transformers import SentenceTransformer
import torch

print("🚀 Downloading multilingual-e5-large...")
print("This may take a while depending on your internet connection...")

try:
    # Tải model với local_files_only=False để download
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
    print(f"   Dimension: {embedding.shape[0]}")
    print(f"   Sample values: {embedding[:5]}")
    
except Exception as e:
    print(f"❌ Error downloading model: {e}")
    print("Please check your internet connection and try again.")
"""
        
        # Tạo file script tạm
        script_file = "temp_download_embedding.py"
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script)
        
        # Chạy script
        result = subprocess.run([sys.executable, script_file], 
                              capture_output=True, text=True)
        
        # Xóa file script tạm
        os.remove(script_file)
        
        if result.returncode == 0:
            print("✅ Embedding model downloaded successfully!")
            print(result.stdout)
        else:
            print("❌ Error downloading embedding model:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error in download process: {e}")
        return False
    
    return True

def verify_model():
    """Kiểm tra model đã tải"""
    model_path = Path("models/embedding")
    
    print("\n🔍 Verifying downloaded model...")
    
    if not model_path.exists():
        print("❌ Model directory not found")
        return False
    
    # Kiểm tra các file cần thiết
    required_files = [
        "config.json",
        "pytorch_model.bin",
        "sentence_bert_config.json",
        "special_tokens_map.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not (model_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required model files found")
    
    # Test load model
    try:
        script = """
from sentence_transformers import SentenceTransformer
import os

print("🧪 Testing model loading...")
model = SentenceTransformer('models/embedding', local_files_only=True)
print("✅ Model loaded successfully from local files")

# Test embedding
test_text = "Test embedding generation"
embedding = model.encode(test_text)
print(f"✅ Test embedding: shape {embedding.shape}, dimension {embedding.shape[0]}")
"""
        
        script_file = "temp_test_model.py"
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script)
        
        result = subprocess.run([sys.executable, script_file], 
                              capture_output=True, text=True)
        
        os.remove(script_file)
        
        if result.returncode == 0:
            print("✅ Model verification passed!")
            print(result.stdout)
            return True
        else:
            print("❌ Model verification failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error verifying model: {e}")
        return False

def check_dependencies():
    """Kiểm tra dependencies"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "sentence-transformers",
        "torch",
        "transformers",
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
                sys.executable, "-m", "pip", "install", 
                "sentence-transformers", "torch", "transformers", "numpy"
            ])
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    return True

def main():
    """Main setup function"""
    print("🤖 Embedding Model Setup")
    print("=" * 50)
    print("Setting up intfloat/multilingual-e5-large for offline use")
    print("=" * 50)
    
    # Kiểm tra dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return
    
    # Tải model
    if not download_embedding_model():
        print("❌ Model download failed")
        return
    
    # Kiểm tra model
    if not verify_model():
        print("❌ Model verification failed")
        return
    
    print("\n" + "=" * 50)
    print("✅ Embedding model setup completed successfully!")
    print("=" * 50)
    print("Model location: models/embedding/")
    print("You can now use the embedding service offline.")
    print("\nTo test the model, run:")
    print("python test_vector_integration.py")

if __name__ == "__main__":
    main()
