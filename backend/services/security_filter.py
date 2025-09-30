"""
Security Filter Service
Kiểm tra câu hỏi có liên quan đến An ninh An toàn thông tin (ATTT)
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SecurityFilter:
    """Service kiểm tra câu hỏi có liên quan đến ATTT"""
    
    def __init__(self):
        # Từ khóa chính về ATTT
        self.security_keywords = {
            # Bảo mật cơ bản
            "bảo mật", "an toàn thông tin", "attt", "cybersecurity", "security",
            "bảo vệ thông tin", "bảo vệ dữ liệu", "data protection", "information security",
            
            # Tấn công mạng
            "tấn công mạng", "cyber attack", "hack", "hacker", "hacking",
            "tấn công", "attack", "exploit", "vulnerability", "lỗ hổng bảo mật",
            "malware", "mã độc", "virus", "trojan", "worm", "spyware",
            "ransomware", "phishing", "social engineering", "tấn công phi kỹ thuật",
            
            # Mã hóa và bảo mật
            "mã hóa", "encryption", "decryption", "cryptography", "crypto",
            "hash", "băm", "digital signature", "chữ ký số", "certificate",
            "ssl", "tls", "https", "vpn", "firewall", "tường lửa",
            
            # SOC và giám sát
            "soc", "security operations center", "trung tâm điều hành an ninh",
            "siem", "security information and event management",
            "monitoring", "giám sát", "log analysis", "phân tích log",
            "incident response", "phản ứng sự cố", "forensics", "điều tra số",
            
            # Penetration testing
            "pentest", "penetration testing", "kiểm thử xâm nhập",
            "vulnerability assessment", "đánh giá lỗ hổng",
            "security audit", "kiểm toán bảo mật", "security testing",
            
            # Compliance và tiêu chuẩn
            "iso 27001", "pci dss", "gdpr", "hipaa", "sox",
            "compliance", "tuân thủ", "tiêu chuẩn bảo mật",
            "security policy", "chính sách bảo mật", "security framework",
            
            # Network security
            "network security", "bảo mật mạng", "network monitoring",
            "intrusion detection", "phát hiện xâm nhập", "ids", "ips",
            "ddos", "denial of service", "từ chối dịch vụ",
            
            # Application security
            "application security", "bảo mật ứng dụng", "web security",
            "owasp", "sql injection", "xss", "csrf", "buffer overflow",
            "secure coding", "lập trình an toàn", "code review",
            
            # Identity and access management
            "iam", "identity and access management", "quản lý danh tính",
            "authentication", "xác thực", "authorization", "phân quyền",
            "single sign on", "sso", "multi factor authentication", "mfa",
            "privileged access management", "pam",
            
            # Cloud security
            "cloud security", "bảo mật đám mây", "aws security", "azure security",
            "container security", "bảo mật container", "kubernetes security",
            
            # Mobile security
            "mobile security", "bảo mật di động", "android security", "ios security",
            "app security", "bảo mật ứng dụng di động",
            
            # IoT security
            "iot security", "bảo mật iot", "internet of things security",
            "embedded security", "bảo mật nhúng",
            
            # Risk management
            "risk management", "quản lý rủi ro", "security risk", "rủi ro bảo mật",
            "threat modeling", "mô hình hóa mối đe dọa", "risk assessment",
            
            # Security awareness
            "security awareness", "nhận thức bảo mật", "security training",
            "đào tạo bảo mật", "security education", "giáo dục bảo mật"
        }
        
        # Từ khóa loại trừ (không liên quan đến ATTT)
        self.exclusion_keywords = {
            "thời tiết", "weather", "thể thao", "sport", "giải trí", "entertainment",
            "nấu ăn", "cooking", "du lịch", "travel", "mua sắm", "shopping",
            "y tế", "medical", "giáo dục", "education", "kinh tế", "economy",
            "chính trị", "politics", "văn hóa", "culture", "lịch sử", "history"
        }
        
        # Cụm từ đặc biệt về ATTT
        self.security_phrases = [
            "an toàn thông tin", "bảo mật thông tin", "cyber security",
            "tấn công mạng", "bảo vệ dữ liệu", "mã hóa dữ liệu",
            "phát hiện xâm nhập", "phản ứng sự cố", "kiểm thử bảo mật",
            "đánh giá rủi ro", "quản lý bảo mật", "chính sách bảo mật",
            "tuân thủ bảo mật", "giám sát bảo mật", "điều tra số",
            "phân tích mối đe dọa", "bảo mật ứng dụng", "bảo mật mạng",
            "bảo mật đám mây", "bảo mật di động", "bảo mật iot"
        ]
        
        logger.info("Security Filter initialized with security keywords and phrases")

    def is_security_related(self, question: str) -> bool:
        """
        Kiểm tra câu hỏi có liên quan đến ATTT hay không
        
        Args:
            question: Câu hỏi cần kiểm tra
            
        Returns:
            bool: True nếu liên quan đến ATTT, False nếu không
        """
        try:
            if not question or not question.strip():
                return False
            
            # Chuẩn hóa câu hỏi
            normalized_question = self._normalize_text(question)
            
            # Kiểm tra từ khóa loại trừ trước
            if self._contains_exclusion_keywords(normalized_question):
                logger.debug(f"Question contains exclusion keywords: {question[:50]}...")
                return False
            
            # Kiểm tra cụm từ đặc biệt về ATTT
            if self._contains_security_phrases(normalized_question):
                logger.debug(f"Question contains security phrases: {question[:50]}...")
                return True
            
            # Kiểm tra từ khóa ATTT
            if self._contains_security_keywords(normalized_question):
                logger.debug(f"Question contains security keywords: {question[:50]}...")
                return True
            
            # Kiểm tra ngữ cảnh ATTT
            if self._has_security_context(normalized_question):
                logger.debug(f"Question has security context: {question[:50]}...")
                return True
            
            logger.debug(f"Question not related to security: {question[:50]}...")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking security relevance: {e}")
            # Trong trường hợp lỗi, cho phép xử lý để tránh block câu hỏi
            return True

    def _normalize_text(self, text: str) -> str:
        """
        Chuẩn hóa text để so sánh
        """
        # Chuyển về chữ thường
        text = text.lower()
        
        # Loại bỏ dấu câu và ký tự đặc biệt
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def _contains_exclusion_keywords(self, text: str) -> bool:
        """
        Kiểm tra có chứa từ khóa loại trừ không
        """
        for keyword in self.exclusion_keywords:
            if keyword in text:
                return True
        return False

    def _contains_security_phrases(self, text: str) -> bool:
        """
        Kiểm tra có chứa cụm từ đặc biệt về ATTT không
        """
        for phrase in self.security_phrases:
            if phrase in text:
                return True
        return False

    def _contains_security_keywords(self, text: str) -> bool:
        """
        Kiểm tra có chứa từ khóa ATTT không
        """
        words = text.split()
        
        # Kiểm tra từng từ
        for word in words:
            if word in self.security_keywords:
                return True
        
        # Kiểm tra cụm từ 2-3 từ
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if bigram in self.security_keywords:
                return True
        
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            if trigram in self.security_keywords:
                return True
        
        return False

    def _has_security_context(self, text: str) -> bool:
        """
        Kiểm tra ngữ cảnh ATTT dựa trên pattern
        """
        # Pattern cho câu hỏi về bảo mật
        security_patterns = [
            r'\b(how to|how do|cách|làm thế nào)\s+(secure|protect|bảo mật|bảo vệ)',
            r'\b(what is|gì là|khái niệm)\s+(security|bảo mật|an toàn)',
            r'\b(why|tại sao)\s+(security|bảo mật|an toàn)',
            r'\b(security|bảo mật|an toàn)\s+(best practice|thực hành tốt)',
            r'\b(security|bảo mật|an toàn)\s+(risk|rủi ro|threat|mối đe dọa)',
            r'\b(security|bảo mật|an toàn)\s+(policy|chính sách|framework)',
            r'\b(security|bảo mật|an toàn)\s+(audit|kiểm toán|assessment|đánh giá)',
            r'\b(security|bảo mật|an toàn)\s+(incident|sự cố|breach|vi phạm)',
            r'\b(security|bảo mật|an toàn)\s+(training|đào tạo|awareness|nhận thức)',
            r'\b(security|bảo mật|an toàn)\s+(compliance|tuân thủ|standard|tiêu chuẩn)'
        ]
        
        for pattern in security_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False

    def get_security_keywords_found(self, question: str) -> List[str]:
        """
        Lấy danh sách từ khóa ATTT được tìm thấy trong câu hỏi
        
        Args:
            question: Câu hỏi cần phân tích
            
        Returns:
            List[str]: Danh sách từ khóa ATTT được tìm thấy
        """
        try:
            if not question or not question.strip():
                return []
            
            normalized_question = self._normalize_text(question)
            found_keywords = []
            
            # Tìm từ khóa đơn
            words = normalized_question.split()
            for word in words:
                if word in self.security_keywords:
                    found_keywords.append(word)
            
            # Tìm cụm từ
            for phrase in self.security_phrases:
                if phrase in normalized_question:
                    found_keywords.append(phrase)
            
            # Tìm bigram và trigram
            for i in range(len(words) - 1):
                bigram = f"{words[i]} {words[i+1]}"
                if bigram in self.security_keywords:
                    found_keywords.append(bigram)
            
            for i in range(len(words) - 2):
                trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
                if trigram in self.security_keywords:
                    found_keywords.append(trigram)
            
            return list(set(found_keywords))  # Loại bỏ trùng lặp
            
        except Exception as e:
            logger.error(f"❌ Error getting security keywords: {e}")
            return []

    def get_security_domain(self, question: str) -> Optional[str]:
        """
        Xác định lĩnh vực ATTT của câu hỏi
        
        Args:
            question: Câu hỏi cần phân tích
            
        Returns:
            Optional[str]: Lĩnh vực ATTT hoặc None
        """
        try:
            if not question or not question.strip():
                return None
            
            normalized_question = self._normalize_text(question)
            
            # Định nghĩa các lĩnh vực ATTT
            security_domains = {
                "Network Security": ["network", "mạng", "firewall", "tường lửa", "vpn", "ddos"],
                "Application Security": ["application", "ứng dụng", "web", "owasp", "sql injection", "xss"],
                "Data Protection": ["data", "dữ liệu", "encryption", "mã hóa", "backup", "sao lưu"],
                "Identity Management": ["identity", "danh tính", "authentication", "xác thực", "iam", "sso"],
                "Incident Response": ["incident", "sự cố", "response", "phản ứng", "forensics", "điều tra"],
                "Risk Management": ["risk", "rủi ro", "threat", "mối đe dọa", "assessment", "đánh giá"],
                "Compliance": ["compliance", "tuân thủ", "iso 27001", "pci dss", "gdpr", "audit"],
                "Security Operations": ["soc", "monitoring", "giám sát", "siem", "log", "nhật ký"],
                "Penetration Testing": ["pentest", "penetration", "kiểm thử", "vulnerability", "lỗ hổng"],
                "Security Awareness": ["awareness", "nhận thức", "training", "đào tạo", "education"]
            }
            
            # Tìm lĩnh vực phù hợp
            for domain, keywords in security_domains.items():
                for keyword in keywords:
                    if keyword in normalized_question:
                        return domain
            
            return "General Security"
            
        except Exception as e:
            logger.error(f"❌ Error getting security domain: {e}")
            return None

    def get_filter_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê về security filter
        
        Returns:
            Dict[str, Any]: Thống kê
        """
        return {
            "total_security_keywords": len(self.security_keywords),
            "total_exclusion_keywords": len(self.exclusion_keywords),
            "total_security_phrases": len(self.security_phrases),
            "security_domains": [
                "Network Security", "Application Security", "Data Protection",
                "Identity Management", "Incident Response", "Risk Management",
                "Compliance", "Security Operations", "Penetration Testing",
                "Security Awareness", "General Security"
            ]
        }

# Global security filter instance
security_filter = SecurityFilter()
