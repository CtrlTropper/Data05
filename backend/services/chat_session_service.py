"""
Chat Session Service
Quản lý các đoạn chat (chat sessions) và lịch sử tin nhắn
"""

import uuid
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

class ChatMessage:
    """Model cho một tin nhắn trong chat"""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role  # "user" hoặc "assistant"
        self.content = content
        self.timestamp = timestamp or datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Tạo từ dictionary"""
        timestamp = datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(timezone.utc)
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=timestamp
        )

class ChatSession:
    """Model cho một đoạn chat"""
    
    def __init__(self, session_id: str, title: Optional[str] = None, created_at: Optional[datetime] = None):
        self.session_id = session_id
        self.title = title or f"Chat Session {session_id[:8]}"
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.messages: List[ChatMessage] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str) -> None:
        """Thêm tin nhắn vào session"""
        message = ChatMessage(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc)
        
        # Auto-generate title from first user message
        if not self.title or self.title.startswith("Chat Session"):
            if role == "user" and len(self.messages) == 1:
                # Use first 50 characters of first user message as title
                self.title = content[:50] + "..." if len(content) > 50 else content
    
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lấy danh sách tin nhắn"""
        messages = self.messages
        if limit:
            messages = messages[-limit:]  # Get last N messages
        return [msg.to_dict() for msg in messages]
    
    def get_message_count(self) -> int:
        """Lấy số lượng tin nhắn"""
        return len(self.messages)
    
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary"""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "message_count": self.get_message_count(),
            "metadata": self.metadata
        }
    
    def to_dict_with_messages(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary bao gồm tin nhắn"""
        data = self.to_dict()
        data["messages"] = self.get_messages(limit)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Tạo từ dictionary"""
        session = cls(
            session_id=data["session_id"],
            title=data.get("title"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(timezone.utc)
        )
        session.updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(timezone.utc)
        session.metadata = data.get("metadata", {})
        
        # Load messages
        for msg_data in data.get("messages", []):
            session.messages.append(ChatMessage.from_dict(msg_data))
        
        return session

class ChatSessionService:
    """Service quản lý chat sessions"""
    
    def __init__(self, storage_file: str = "data/chat_sessions.json"):
        self.storage_file = Path(storage_file)
        self.sessions: Dict[str, ChatSession] = {}
        self._lock = asyncio.Lock()
        
        # Ensure storage directory exists
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ChatSessionService initialized with storage: {self.storage_file}")
    
    async def initialize(self):
        """Khởi tạo service và load dữ liệu từ file"""
        try:
            await self._load_sessions()
            logger.info(f"✅ Loaded {len(self.sessions)} chat sessions")
        except Exception as e:
            logger.error(f"❌ Error loading chat sessions: {e}")
            self.sessions = {}
    
    async def create_session(self, title: Optional[str] = None) -> str:
        """Tạo session mới"""
        async with self._lock:
            session_id = str(uuid.uuid4())
            session = ChatSession(session_id=session_id, title=title)
            self.sessions[session_id] = session
            
            # Save to file
            await self._save_sessions()
            
            logger.info(f"✅ Created new chat session: {session_id}")
            return session_id
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Lấy session theo ID"""
        return self.sessions.get(session_id)
    
    async def list_sessions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Liệt kê các sessions"""
        sessions = list(self.sessions.values())
        
        # Sort by updated_at (newest first)
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        
        if limit:
            sessions = sessions[:limit]
        
        return [session.to_dict() for session in sessions]
    
    async def delete_session(self, session_id: str) -> bool:
        """Xóa session"""
        async with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                await self._save_sessions()
                logger.info(f"✅ Deleted chat session: {session_id}")
                return True
            else:
                logger.warning(f"⚠️ Session not found: {session_id}")
                return False
    
    async def add_message(self, session_id: str, role: str, content: str) -> bool:
        """Thêm tin nhắn vào session"""
        async with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                logger.warning(f"⚠️ Session not found: {session_id}")
                return False
            
            session.add_message(role=role, content=content)
            await self._save_sessions()
            
            logger.debug(f"✅ Added message to session {session_id}: {role}")
            return True
    
    async def get_session_messages(self, session_id: str, limit: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """Lấy tin nhắn của session"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        return session.get_messages(limit)
    
    async def get_session_with_messages(self, session_id: str, limit: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Lấy session với tin nhắn"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        return session.to_dict_with_messages(limit)
    
    async def update_session_metadata(self, session_id: str, metadata: Dict[str, Any]) -> bool:
        """Cập nhật metadata của session"""
        async with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            session.metadata.update(metadata)
            session.updated_at = datetime.now(timezone.utc)
            await self._save_sessions()
            
            return True
    
    async def clear_all_sessions(self) -> int:
        """Xóa tất cả sessions"""
        async with self._lock:
            count = len(self.sessions)
            self.sessions.clear()
            await self._save_sessions()
            
            logger.info(f"✅ Cleared all {count} chat sessions")
            return count
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Lấy thống kê sessions"""
        total_sessions = len(self.sessions)
        total_messages = sum(session.get_message_count() for session in self.sessions.values())
        
        # Get recent sessions (last 7 days)
        recent_sessions = 0
        week_ago = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = week_ago.replace(day=week_ago.day - 7)
        
        for session in self.sessions.values():
            if session.updated_at >= week_ago:
                recent_sessions += 1
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "recent_sessions": recent_sessions,
            "storage_file": str(self.storage_file),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    async def _load_sessions(self):
        """Load sessions từ file"""
        if not self.storage_file.exists():
            logger.info("No existing chat sessions file found, starting fresh")
            return
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.sessions = {}
            for session_data in data.get("sessions", []):
                session = ChatSession.from_dict(session_data)
                self.sessions[session.session_id] = session
            
            logger.info(f"✅ Loaded {len(self.sessions)} chat sessions from {self.storage_file}")
            
        except Exception as e:
            logger.error(f"❌ Error loading chat sessions from {self.storage_file}: {e}")
            self.sessions = {}
    
    async def _save_sessions(self):
        """Lưu sessions vào file"""
        try:
            data = {
                "sessions": [session.to_dict_with_messages() for session in self.sessions.values()],
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "version": "1.0"
            }
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = self.storage_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_file.replace(self.storage_file)
            
            logger.debug(f"✅ Saved {len(self.sessions)} chat sessions to {self.storage_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving chat sessions to {self.storage_file}: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup khi shutdown"""
        logger.info("🧹 Cleaning up ChatSessionService...")
        try:
            await self._save_sessions()
            logger.info("✅ ChatSessionService cleanup complete")
        except Exception as e:
            logger.error(f"❌ Error during ChatSessionService cleanup: {e}")

# Global chat session service instance
chat_session_service = ChatSessionService()
