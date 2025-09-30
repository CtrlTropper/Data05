"""
Test script cho Security Filter
Kiểm tra chức năng lọc câu hỏi liên quan đến ATTT
"""

import sys
import os
import asyncio
import logging

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.security_filter import security_filter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_security_filter():
    """Test security filter functionality"""
    print("\n" + "="*60)
    print("🧪 TESTING SECURITY FILTER")
    print("="*60)
    
    # Test cases
    test_cases = [
        # Security-related questions (should return True)
        {
            "question": "Bảo mật thông tin là gì?",
            "expected": True,
            "category": "Basic Security"
        },
        {
            "question": "Làm thế nào để bảo vệ khỏi ransomware?",
            "expected": True,
            "category": "Malware Protection"
        },
        {
            "question": "SOC hoạt động như thế nào?",
            "expected": True,
            "category": "Security Operations"
        },
        {
            "question": "Pentest có những giai đoạn nào?",
            "expected": True,
            "category": "Penetration Testing"
        },
        {
            "question": "Mã hóa dữ liệu quan trọng như thế nào?",
            "expected": True,
            "category": "Cryptography"
        },
        {
            "question": "Tấn công mạng có những loại nào?",
            "expected": True,
            "category": "Cyber Attacks"
        },
        {
            "question": "ISO 27001 là gì?",
            "expected": True,
            "category": "Compliance"
        },
        {
            "question": "Firewall hoạt động như thế nào?",
            "expected": True,
            "category": "Network Security"
        },
        {
            "question": "Phishing là gì và cách phòng chống?",
            "expected": True,
            "category": "Social Engineering"
        },
        {
            "question": "Vulnerability assessment có những bước nào?",
            "expected": True,
            "category": "Risk Assessment"
        },
        
        # Non-security questions (should return False)
        {
            "question": "Thời tiết hôm nay như thế nào?",
            "expected": False,
            "category": "Weather"
        },
        {
            "question": "Cách nấu phở bò?",
            "expected": False,
            "category": "Cooking"
        },
        {
            "question": "Bóng đá World Cup 2022 diễn ra ở đâu?",
            "expected": False,
            "category": "Sports"
        },
        {
            "question": "Du lịch Đà Nẵng có gì hay?",
            "expected": False,
            "category": "Travel"
        },
        {
            "question": "Giá vàng hôm nay bao nhiêu?",
            "expected": False,
            "category": "Finance"
        },
        {
            "question": "Cách học tiếng Anh hiệu quả?",
            "expected": False,
            "category": "Education"
        },
        {
            "question": "Phim hay nhất năm 2023?",
            "expected": False,
            "category": "Entertainment"
        },
        {
            "question": "Cách giảm cân nhanh?",
            "expected": False,
            "category": "Health"
        },
        {
            "question": "Mua nhà ở đâu tốt?",
            "expected": False,
            "category": "Real Estate"
        },
        {
            "question": "Cách chăm sóc cây cảnh?",
            "expected": False,
            "category": "Gardening"
        }
    ]
    
    # Run tests
    passed = 0
    total = len(test_cases)
    
    print(f"Running {total} test cases...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case["question"]
        expected = test_case["expected"]
        category = test_case["category"]
        
        # Test security relevance
        result = security_filter.is_security_related(question)
        
        # Test additional functions
        keywords_found = security_filter.get_security_keywords_found(question)
        security_domain = security_filter.get_security_domain(question)
        
        # Check result
        if result == expected:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
        
        print(f"Test {i:2d}: {status}")
        print(f"  Question: {question}")
        print(f"  Category: {category}")
        print(f"  Expected: {expected}, Got: {result}")
        print(f"  Keywords found: {keywords_found}")
        print(f"  Security domain: {security_domain}")
        print()
    
    # Summary
    print("="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed.")
    
    return passed == total

def test_security_domains():
    """Test security domain classification"""
    print("\n" + "="*60)
    print("🧪 TESTING SECURITY DOMAINS")
    print("="*60)
    
    domain_test_cases = [
        ("Network Security", "Firewall hoạt động như thế nào?"),
        ("Application Security", "OWASP Top 10 là gì?"),
        ("Data Protection", "Mã hóa AES hoạt động ra sao?"),
        ("Identity Management", "Single Sign-On là gì?"),
        ("Incident Response", "Xử lý sự cố bảo mật như thế nào?"),
        ("Risk Management", "Đánh giá rủi ro bảo mật?"),
        ("Compliance", "PCI DSS có những yêu cầu gì?"),
        ("Security Operations", "SIEM hoạt động như thế nào?"),
        ("Penetration Testing", "Kiểm thử xâm nhập có những giai đoạn nào?"),
        ("Security Awareness", "Đào tạo nhận thức bảo mật quan trọng như thế nào?")
    ]
    
    print("Testing security domain classification...\n")
    
    for expected_domain, question in domain_test_cases:
        detected_domain = security_filter.get_security_domain(question)
        
        if detected_domain == expected_domain:
            status = "✅ CORRECT"
        else:
            status = "❌ INCORRECT"
        
        print(f"{status} - Expected: {expected_domain}, Got: {detected_domain}")
        print(f"  Question: {question}")
        print()

def test_keyword_extraction():
    """Test keyword extraction"""
    print("\n" + "="*60)
    print("🧪 TESTING KEYWORD EXTRACTION")
    print("="*60)
    
    keyword_test_cases = [
        "Bảo mật thông tin và tấn công mạng",
        "Ransomware và malware protection",
        "SOC và SIEM monitoring",
        "Pentest và vulnerability assessment",
        "ISO 27001 compliance và audit"
    ]
    
    print("Testing keyword extraction...\n")
    
    for question in keyword_test_cases:
        keywords = security_filter.get_security_keywords_found(question)
        print(f"Question: {question}")
        print(f"Keywords found: {keywords}")
        print()

def test_filter_stats():
    """Test filter statistics"""
    print("\n" + "="*60)
    print("🧪 TESTING FILTER STATISTICS")
    print("="*60)
    
    stats = security_filter.get_filter_stats()
    
    print("Security Filter Statistics:")
    print(f"  Total security keywords: {stats['total_security_keywords']}")
    print(f"  Total exclusion keywords: {stats['total_exclusion_keywords']}")
    print(f"  Total security phrases: {stats['total_security_phrases']}")
    print(f"  Security domains: {len(stats['security_domains'])}")
    print("\nSecurity domains:")
    for domain in stats['security_domains']:
        print(f"  - {domain}")

def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*60)
    print("🧪 TESTING EDGE CASES")
    print("="*60)
    
    edge_cases = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("a", "Single character"),
        ("bảo mật", "Single security keyword"),
        ("thời tiết bảo mật", "Mixed content"),
        ("BẢO MẬT THÔNG TIN", "Uppercase"),
        ("Bảo Mật Thông Tin", "Title case"),
        ("bảo-mật thông-tin", "With hyphens"),
        ("bảo_mật_thông_tin", "With underscores"),
        ("bảo.mật.thông.tin", "With dots")
    ]
    
    print("Testing edge cases...\n")
    
    for test_input, description in edge_cases:
        result = security_filter.is_security_related(test_input)
        print(f"{description}: '{test_input}' -> {result}")

def main():
    """Main test function"""
    print("🚀 SECURITY FILTER TEST")
    print("Testing security question filtering for ATTT chatbot")
    
    # Run all tests
    test_results = []
    
    test_results.append(test_security_filter())
    test_security_domains()
    test_keyword_extraction()
    test_filter_stats()
    test_edge_cases()
    
    # Final summary
    print("\n" + "="*60)
    print("🎯 FINAL SUMMARY")
    print("="*60)
    
    if all(test_results):
        print("🎉 All security filter tests passed!")
        print("✅ Security filter is working correctly.")
        print("✅ Chatbot will only respond to ATTT-related questions.")
    else:
        print("⚠️ Some security filter tests failed.")
        print("❌ Please check the implementation.")

if __name__ == "__main__":
    main()
