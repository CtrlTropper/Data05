"""
Setup script để tải LLM model offline
Script tải gpt-oss-20b về local
"""

import os
import sys
import subprocess
from pathlib import Path

def download_llm_model():
    """Tải LLM model gpt-oss-20b"""
    print("📥 Downloading LLM model (gpt-oss-20b)...")
    
    model_path = Path("models/llm")
    model_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Script để tải model
        script = """
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

print("🚀 Downloading gpt-oss-20b...")
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
    print("Note: gpt-oss-20b is a large model (~40GB) and requires significant disk space.")
"""
        
        # Tạo file script tạm
        script_file = "temp_download_llm.py"
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script)
        
        # Chạy script
        result = subprocess.run([sys.executable, script_file], 
                              capture_output=True, text=True)
        
        # Xóa file script tạm
        os.remove(script_file)
        
        if result.returncode == 0:
            print("✅ LLM model downloaded successfully!")
            print(result.stdout)
        else:
            print("❌ Error downloading LLM model:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error in download process: {e}")
        return False
    
    return True

def verify_model():
    """Kiểm tra model đã tải"""
    model_path = Path("models/llm")
    
    print("\n🔍 Verifying downloaded model...")
    
    if not model_path.exists():
        print("❌ Model directory not found")
        return False
    
    # Kiểm tra các file cần thiết
    required_files = [
        "config.json",
        "pytorch_model.bin",  # hoặc model.safetensors
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.json",
        "merges.txt"
    ]
    
    # Kiểm tra ít nhất một số file cơ bản
    basic_files = ["config.json", "tokenizer_config.json"]
    missing_files = []
    
    for file in basic_files:
        if not (model_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing basic files: {missing_files}")
        return False
    
    print("✅ Basic model files found")
    
    # Test load model
    try:
        script = """
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

print("🧪 Testing model loading...")
try:
    tokenizer = AutoTokenizer.from_pretrained('models/llm', local_files_only=True)
    print("✅ Tokenizer loaded successfully from local files")
    
    # Test model loading (without actually loading the full model to save memory)
    print("Testing model configuration...")
    from transformers import AutoConfig
    config = AutoConfig.from_pretrained('models/llm', local_files_only=True)
    print(f"✅ Model config loaded: {config.model_type}")
    print(f"   Vocab size: {config.vocab_size}")
    print(f"   Hidden size: {config.hidden_size}")
    print(f"   Num layers: {config.num_hidden_layers}")
    
    # Test tokenizer
    test_text = "Hello, this is a test"
    tokens = tokenizer(test_text, return_tensors="pt")
    print(f"✅ Tokenizer test successful: {tokens['input_ids'].shape}")
    
except Exception as e:
    print(f"❌ Model verification failed: {e}")
    raise
"""
        
        script_file = "temp_test_llm.py"
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
        "transformers",
        "torch",
        "accelerate",
        "bitsandbytes"  # For quantization
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
                "transformers", "torch", "accelerate", "bitsandbytes"
            ])
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    return True

def check_gpu():
    """Kiểm tra GPU"""
    print("🔍 Checking GPU availability...")
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            
            print(f"✅ GPU available: {gpu_name}")
            print(f"   GPU count: {gpu_count}")
            print(f"   GPU memory: {gpu_memory:.1f} GB")
            
            if gpu_memory < 12:
                print("⚠️ Warning: GPU memory is less than 12GB. Model may not fit.")
                print("   Consider using quantization (8-bit or 4-bit)")
            
            return True
        else:
            print("❌ No GPU available. Model will run on CPU (very slow)")
            print("   Consider using a GPU-enabled environment")
            return False
            
    except ImportError:
        print("❌ PyTorch not installed")
        return False

def check_disk_space():
    """Kiểm tra dung lượng disk"""
    print("🔍 Checking disk space...")
    
    try:
        import shutil
        
        # Kiểm tra dung lượng còn trống
        total, used, free = shutil.disk_usage(".")
        free_gb = free / 1024**3
        
        print(f"Available disk space: {free_gb:.1f} GB")
        
        if free_gb < 50:
            print("⚠️ Warning: Less than 50GB free space available")
            print("   gpt-oss-20b requires ~40GB for the model")
            return False
        
        print("✅ Sufficient disk space available")
        return True
        
    except Exception as e:
        print(f"❌ Error checking disk space: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 LLM Model Setup")
    print("=" * 50)
    print("Setting up gpt-oss-20b for offline use")
    print("=" * 50)
    
    # Kiểm tra dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return
    
    # Kiểm tra GPU
    gpu_available = check_gpu()
    
    # Kiểm tra disk space
    if not check_disk_space():
        print("❌ Insufficient disk space")
        return
    
    # Tải model
    if not download_llm_model():
        print("❌ Model download failed")
        return
    
    # Kiểm tra model
    if not verify_model():
        print("❌ Model verification failed")
        return
    
    print("\n" + "=" * 50)
    print("✅ LLM model setup completed successfully!")
    print("=" * 50)
    print("Model location: models/llm/")
    print("You can now use the LLM service offline.")
    
    if gpu_available:
        print("\nGPU optimization tips:")
        print("- Use 8-bit quantization for memory efficiency")
        print("- Use 4-bit quantization for maximum memory savings")
        print("- Monitor GPU memory usage during inference")
    
    print("\nTo test the model, run:")
    print("python test_llm_service.py")

if __name__ == "__main__":
    main()
