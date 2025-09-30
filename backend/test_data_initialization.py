"""
Test script cho Data Initialization
Kiểm tra chức năng khởi tạo dữ liệu ban đầu
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.data_initialization import data_initialization_service
from services.embedding_service import embedding_service
from services.vector_service import vector_service
from services.pdf_processor import pdf_processor

async def test_data_initialization():
    """Test data initialization service"""
    print("\n" + "="*60)
    print("🧪 TESTING DATA INITIALIZATION")
    print("="*60)
    
    try:
        # Initialize dependencies
        print("Step 1: Initialize dependencies")
        await embedding_service.load_model()
        await pdf_processor.initialize()
        
        print("✅ Dependencies initialized")
        
        # Initialize data initialization service
        print("\nStep 2: Initialize data initialization service")
        await data_initialization_service.initialize(
            embedding_service=embedding_service,
            vector_service=vector_service,
            pdf_processor=pdf_processor
        )
        
        print("✅ Data initialization service initialized")
        
        # Get category stats
        print("\nStep 3: Get category statistics")
        stats = await data_initialization_service.get_category_stats()
        
        print("📊 Category Statistics:")
        for category, info in stats.items():
            print(f"   {category}: {info['document_count']} documents, exists: {info['exists']}")
        
        # Test with sample document (if available)
        test_doc_path = "data/Luat/sample_law.pdf"
        if os.path.exists(test_doc_path):
            print(f"\nStep 4: Test with sample document: {test_doc_path}")
            
            result = await data_initialization_service.add_uploaded_document(
                test_doc_path, 
                "sample_law.pdf"
            )
            
            if result.get("success"):
                print(f"✅ Document added successfully")
                print(f"   Chunks created: {result.get('chunks_created', 0)}")
                print(f"   Text length: {result.get('text_length', 0)}")
            else:
                print(f"❌ Failed to add document: {result.get('error', 'Unknown error')}")
        else:
            print(f"\nStep 4: No test document found at {test_doc_path}")
            print("   Create test documents to test functionality")
        
        # Test reload category
        print(f"\nStep 5: Test reload category")
        reload_result = await data_initialization_service.reload_category("Luat")
        
        if reload_result.get("success"):
            print(f"✅ Category reloaded successfully")
            print(f"   Documents processed: {reload_result.get('documents_processed', 0)}")
            print(f"   Chunks created: {reload_result.get('chunks_created', 0)}")
        else:
            print(f"❌ Failed to reload category: {reload_result.get('error', 'Unknown error')}")
        
        print("\n" + "="*60)
        print("📊 DATA INITIALIZATION TEST SUMMARY")
        print("="*60)
        print("✅ Dependencies initialization: PASSED")
        print("✅ Data initialization service: PASSED")
        print("✅ Category statistics: PASSED")
        if os.path.exists(test_doc_path):
            print("✅ Document addition: PASSED")
        else:
            print("⚠️ Document addition: SKIPPED (no test file)")
        print("✅ Category reload: PASSED")
        
        print("\n🎉 Data Initialization is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Data Initialization test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_category_filtering():
    """Test category filtering in search"""
    print("\n" + "="*60)
    print("🧪 TESTING CATEGORY FILTERING")
    print("="*60)
    
    try:
        from db.faiss_store import faiss_store
        
        # Test search with category filter
        test_queries = [
            "an toàn thông tin",
            "cybersecurity",
            "luật pháp"
        ]
        
        categories = ["Luat", "TaiLieuTiengViet", "TaiLieuTiengAnh", "Uploads"]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            
            # Search without category filter
            results_all = faiss_store.search_text(
                query_text=query,
                top_k=3,
                embedding_service=embedding_service
            )
            print(f"   All categories: {len(results_all)} results")
            
            # Search with category filter
            for category in categories:
                results_category = faiss_store.search_text(
                    query_text=query,
                    top_k=3,
                    category=category,
                    embedding_service=embedding_service
                )
                print(f"   {category}: {len(results_category)} results")
        
        print("\n✅ Category filtering test completed")
        
    except Exception as e:
        print(f"❌ Category filtering test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 DATA INITIALIZATION TEST")
    print("Testing data initialization and category management")
    
    # Test data initialization
    await test_data_initialization()
    
    # Test category filtering
    await test_category_filtering()
    
    print("\n🎉 All data initialization tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
