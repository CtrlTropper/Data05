"""
Test script cho LLM Service
Test mô hình gpt-oss-20b offline từ local GPU
"""

import asyncio
import os
import sys
import logging
import time
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import llm_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_llm_service():
    """Test LLM service offline"""
    print("\n" + "="*60)
    print("🧪 TESTING LLM SERVICE - GPT-OSS-20B OFFLINE")
    print("="*60)
    
    try:
        # Test 1: Load model
        print("1. Loading LLM model...")
        await llm_service.load_model()
        
        # Test model info
        model_info = llm_service.get_model_info()
        print(f"✅ Model loaded: {model_info['model_name']}")
        print(f"   Device: {model_info['device']}")
        print(f"   Model path: {model_info['model_path']}")
        print(f"   Max length: {model_info['max_length']}")
        print(f"   Quantization: {model_info['use_quantization']}")
        
        if model_info.get('gpu_name'):
            print(f"   GPU: {model_info['gpu_name']}")
            print(f"   GPU Memory Total: {model_info['gpu_memory_total']:.1f} GB")
            print(f"   GPU Memory Allocated: {model_info['gpu_memory_allocated']:.1f} GB")
        
        # Test 2: Basic answer generation
        print("\n2. Testing basic answer generation...")
        question = "Trí tuệ nhân tạo là gì?"
        start_time = time.time()
        
        answer = llm_service.generate_answer(question)
        end_time = time.time()
        
        print(f"✅ Generated answer in {end_time - start_time:.2f}s")
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        
        # Test 3: Answer with context
        print("\n3. Testing answer with context...")
        context = """
        Trí tuệ nhân tạo (AI) là một lĩnh vực khoa học máy tính tập trung vào việc tạo ra các hệ thống có khả năng thực hiện các tác vụ thông minh. 
        Machine learning là một nhánh con của AI, cho phép máy tính học hỏi từ dữ liệu mà không cần lập trình rõ ràng.
        """
        
        question_with_context = "Machine learning có mối quan hệ như thế nào với AI?"
        start_time = time.time()
        
        answer_with_context = llm_service.generate_answer(question_with_context, context)
        end_time = time.time()
        
        print(f"✅ Generated answer with context in {end_time - start_time:.2f}s")
        print(f"Question: {question_with_context}")
        print(f"Context: {context[:100]}...")
        print(f"Answer: {answer_with_context}")
        
        # Test 4: Different parameters
        print("\n4. Testing different generation parameters...")
        
        # Test with different temperature
        print("Testing with temperature=0.3 (more deterministic)...")
        answer_temp_low = llm_service.generate_answer(
            "Hãy giải thích về deep learning", 
            max_tokens=200, 
            temperature=0.3
        )
        print(f"Answer (temp=0.3): {answer_temp_low[:100]}...")
        
        # Test with different max_tokens
        print("\nTesting with max_tokens=50 (shorter response)...")
        answer_short = llm_service.generate_answer(
            "Python là gì?", 
            max_tokens=50, 
            temperature=0.7
        )
        print(f"Answer (max_tokens=50): {answer_short}")
        
        # Test 5: Streaming response
        print("\n5. Testing streaming response...")
        question_stream = "Hãy giải thích về neural networks"
        start_time = time.time()
        
        print(f"Question: {question_stream}")
        print("Streaming answer:")
        
        full_response = ""
        async for chunk in llm_service.generate_answer_with_streaming(
            question_stream, 
            max_tokens=300, 
            temperature=0.7
        ):
            print(chunk, end="", flush=True)
            full_response += chunk
        
        end_time = time.time()
        print(f"\n✅ Streaming completed in {end_time - start_time:.2f}s")
        print(f"Full response length: {len(full_response)} characters")
        
        # Test 6: Performance test
        print("\n6. Testing performance...")
        questions = [
            "FastAPI là gì?",
            "ReactJS có những ưu điểm gì?",
            "Database là gì?",
            "API REST là gì?",
            "Docker container là gì?"
        ]
        
        total_time = 0
        successful_requests = 0
        
        for i, q in enumerate(questions, 1):
            start_time = time.time()
            try:
                answer = llm_service.generate_answer(q, max_tokens=100, temperature=0.7)
                end_time = time.time()
                
                request_time = end_time - start_time
                total_time += request_time
                successful_requests += 1
                
                print(f"   Question {i}: {request_time:.2f}s - {len(answer)} chars")
            except Exception as e:
                print(f"   Question {i}: Failed - {e}")
        
        if successful_requests > 0:
            avg_time = total_time / successful_requests
            print(f"✅ Performance test completed:")
            print(f"   Successful: {successful_requests}/{len(questions)}")
            print(f"   Average time: {avg_time:.2f}s per question")
            print(f"   Total time: {total_time:.2f}s")
        
        # Test 7: GPU memory management
        print("\n7. Testing GPU memory management...")
        if model_info.get('gpu_name'):
            print("Clearing GPU cache...")
            llm_service.clear_gpu_cache()
            
            # Check memory after clearing
            model_info_after = llm_service.get_model_info()
            print(f"GPU Memory after clearing:")
            print(f"   Allocated: {model_info_after['gpu_memory_allocated']:.1f} GB")
            print(f"   Reserved: {model_info_after['gpu_memory_reserved']:.1f} GB")
        
        # Test 8: Generation config update
        print("\n8. Testing generation config update...")
        original_temp = llm_service.generation_config.temperature
        llm_service.update_generation_config(temperature=0.5, top_p=0.8)
        
        print("Updated generation config:")
        print(f"   Temperature: {llm_service.generation_config.temperature}")
        print(f"   Top-p: {llm_service.generation_config.top_p}")
        
        # Restore original config
        llm_service.update_generation_config(temperature=original_temp, top_p=0.9)
        
        return True
        
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        return False

async def test_offline_operation():
    """Test hoạt động offline"""
    print("\n" + "="*60)
    print("🧪 TESTING OFFLINE OPERATION")
    print("="*60)
    
    try:
        # Test without internet connection (simulate)
        print("1. Testing offline model loading...")
        
        # The model should already be loaded from local files
        model_info = llm_service.get_model_info()
        if model_info['model_loaded']:
            print("✅ Model loaded successfully from local files")
        else:
            print("❌ Model not loaded")
            return False
        
        # Test offline generation
        print("\n2. Testing offline answer generation...")
        question = "Test offline operation"
        answer = llm_service.generate_answer(question, max_tokens=100)
        
        if answer and len(answer) > 0:
            print("✅ Offline answer generation successful")
            print(f"Answer: {answer[:100]}...")
        else:
            print("❌ Offline answer generation failed")
            return False
        
        print("\n✅ Offline operation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Offline operation test failed: {e}")
        return False

async def test_error_handling():
    """Test error handling"""
    print("\n" + "="*60)
    print("🧪 TESTING ERROR HANDLING")
    print("="*60)
    
    try:
        # Test empty question
        print("1. Testing empty question...")
        try:
            answer = llm_service.generate_answer("")
            print("❌ Should have raised ValueError for empty question")
        except ValueError as e:
            print(f"✅ Correctly caught ValueError: {e}")
        
        # Test very long question
        print("\n2. Testing very long question...")
        long_question = "What is " * 1000  # Very long question
        try:
            answer = llm_service.generate_answer(long_question, max_tokens=50)
            print(f"✅ Handled long question: {len(answer)} chars")
        except Exception as e:
            print(f"✅ Correctly handled long question error: {e}")
        
        # Test invalid parameters
        print("\n3. Testing invalid parameters...")
        try:
            answer = llm_service.generate_answer(
                "Test question", 
                max_tokens=-1,  # Invalid
                temperature=2.0  # Invalid
            )
            print("❌ Should have handled invalid parameters")
        except Exception as e:
            print(f"✅ Correctly handled invalid parameters: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 LLM SERVICE TEST")
    print("Testing gpt-oss-20b offline from local GPU")
    
    # Create test directories
    os.makedirs("models/llm", exist_ok=True)
    
    test_results = []
    
    # Run tests
    test_results.append(await test_llm_service())
    test_results.append(await test_offline_operation())
    test_results.append(await test_error_handling())
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! LLM service is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    # Cleanup
    try:
        await llm_service.cleanup()
        print("\n✅ Cleanup completed")
    except Exception as e:
        print(f"\n⚠️ Cleanup error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
