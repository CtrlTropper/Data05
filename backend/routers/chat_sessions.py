"""
Chat Sessions Router
Router xử lý quản lý các đoạn chat (chat sessions)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

# Import services
from services.chat_session_service import chat_session_service

logger = logging.getLogger(__name__)
router = APIRouter()

class CreateSessionRequest(BaseModel):
    """Request model cho tạo session mới"""
    title: Optional[str] = None

class CreateSessionResponse(BaseModel):
    """Response model cho tạo session mới"""
    session_id: str
    title: str
    created_at: str
    message_count: int

class SessionInfo(BaseModel):
    """Model cho thông tin session"""
    session_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    metadata: Dict[str, Any]

class SessionWithMessages(BaseModel):
    """Model cho session với tin nhắn"""
    session_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    metadata: Dict[str, Any]
    messages: List[Dict[str, Any]]

class SessionStats(BaseModel):
    """Model cho thống kê sessions"""
    total_sessions: int
    total_messages: int
    recent_sessions: int
    storage_file: str
    last_updated: str

@router.post("/chat_sessions", response_model=CreateSessionResponse)
async def create_chat_session(request: CreateSessionRequest) -> CreateSessionResponse:
    """
    Tạo đoạn chat mới
    
    Args:
        request: Thông tin tạo session
        
    Returns:
        CreateSessionResponse: Thông tin session mới
    """
    try:
        session_id = await chat_session_service.create_session(title=request.title)
        session = await chat_session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        logger.info(f"✅ Created new chat session: {session_id}")
        
        return CreateSessionResponse(
            session_id=session.session_id,
            title=session.title,
            created_at=session.created_at.isoformat(),
            message_count=session.get_message_count()
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating chat session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tạo session: {str(e)}"
        )

@router.get("/chat_sessions", response_model=List[SessionInfo])
async def list_chat_sessions(
    limit: Optional[int] = Query(None, description="Số lượng sessions tối đa", ge=1, le=100)
) -> List[SessionInfo]:
    """
    Liệt kê các đoạn chat đang có
    
    Args:
        limit: Số lượng sessions tối đa
        
    Returns:
        List[SessionInfo]: Danh sách sessions
    """
    try:
        sessions_data = await chat_session_service.list_sessions(limit=limit)
        
        sessions = []
        for session_data in sessions_data:
            sessions.append(SessionInfo(**session_data))
        
        logger.info(f"✅ Listed {len(sessions)} chat sessions")
        return sessions
        
    except Exception as e:
        logger.error(f"❌ Error listing chat sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi liệt kê sessions: {str(e)}"
        )

@router.get("/chat_sessions/{session_id}", response_model=SessionWithMessages)
async def get_chat_session(
    session_id: str,
    limit: Optional[int] = Query(None, description="Số lượng tin nhắn tối đa", ge=1, le=1000)
) -> SessionWithMessages:
    """
    Lấy thông tin chi tiết của một session
    
    Args:
        session_id: ID của session
        limit: Số lượng tin nhắn tối đa
        
    Returns:
        SessionWithMessages: Thông tin session với tin nhắn
    """
    try:
        session_data = await chat_session_service.get_session_with_messages(session_id, limit=limit)
        
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail=f"Session không tồn tại: {session_id}"
            )
        
        logger.info(f"✅ Retrieved chat session: {session_id}")
        return SessionWithMessages(**session_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting chat session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy session: {str(e)}"
        )

@router.delete("/chat_sessions/{session_id}")
async def delete_chat_session(session_id: str) -> Dict[str, Any]:
    """
    Xóa một đoạn chat theo session_id
    
    Args:
        session_id: ID của session cần xóa
        
    Returns:
        Dict[str, Any]: Kết quả xóa
    """
    try:
        success = await chat_session_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session không tồn tại: {session_id}"
            )
        
        logger.info(f"✅ Deleted chat session: {session_id}")
        return {
            "message": "Session đã được xóa thành công",
            "session_id": session_id,
            "deleted": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting chat session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xóa session: {str(e)}"
        )

@router.get("/chat_sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: Optional[int] = Query(None, description="Số lượng tin nhắn tối đa", ge=1, le=1000)
) -> List[Dict[str, Any]]:
    """
    Lấy tin nhắn của một session
    
    Args:
        session_id: ID của session
        limit: Số lượng tin nhắn tối đa
        
    Returns:
        List[Dict[str, Any]]: Danh sách tin nhắn
    """
    try:
        messages = await chat_session_service.get_session_messages(session_id, limit=limit)
        
        if messages is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session không tồn tại: {session_id}"
            )
        
        logger.info(f"✅ Retrieved {len(messages)} messages from session: {session_id}")
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting messages for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy tin nhắn: {str(e)}"
        )

@router.post("/chat_sessions/{session_id}/messages")
async def add_message_to_session(
    session_id: str,
    role: str,
    content: str
) -> Dict[str, Any]:
    """
    Thêm tin nhắn vào session
    
    Args:
        session_id: ID của session
        role: Vai trò (user hoặc assistant)
        content: Nội dung tin nhắn
        
    Returns:
        Dict[str, Any]: Kết quả thêm tin nhắn
    """
    try:
        if role not in ["user", "assistant"]:
            raise HTTPException(
                status_code=400,
                detail="Role phải là 'user' hoặc 'assistant'"
            )
        
        if not content or not content.strip():
            raise HTTPException(
                status_code=400,
                detail="Nội dung tin nhắn không được để trống"
            )
        
        success = await chat_session_service.add_message(
            session_id=session_id,
            role=role,
            content=content.strip()
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session không tồn tại: {session_id}"
            )
        
        logger.info(f"✅ Added {role} message to session: {session_id}")
        return {
            "message": "Tin nhắn đã được thêm thành công",
            "session_id": session_id,
            "role": role,
            "content": content.strip(),
            "added": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error adding message to session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi thêm tin nhắn: {str(e)}"
        )

@router.get("/chat_sessions/stats", response_model=SessionStats)
async def get_chat_sessions_stats() -> SessionStats:
    """
    Lấy thống kê về chat sessions
    
    Returns:
        SessionStats: Thống kê sessions
    """
    try:
        stats = await chat_session_service.get_session_stats()
        
        logger.info("✅ Retrieved chat sessions stats")
        return SessionStats(**stats)
        
    except Exception as e:
        logger.error(f"❌ Error getting chat sessions stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy thống kê: {str(e)}"
        )

@router.delete("/chat_sessions")
async def clear_all_chat_sessions() -> Dict[str, Any]:
    """
    Xóa tất cả chat sessions
    
    Returns:
        Dict[str, Any]: Kết quả xóa
    """
    try:
        count = await chat_session_service.clear_all_sessions()
        
        logger.info(f"✅ Cleared all {count} chat sessions")
        return {
            "message": f"Đã xóa {count} sessions thành công",
            "deleted_count": count,
            "cleared": True
        }
        
    except Exception as e:
        logger.error(f"❌ Error clearing all chat sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xóa tất cả sessions: {str(e)}"
        )

@router.put("/chat_sessions/{session_id}/metadata")
async def update_session_metadata(
    session_id: str,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Cập nhật metadata của session
    
    Args:
        session_id: ID của session
        metadata: Metadata cần cập nhật
        
    Returns:
        Dict[str, Any]: Kết quả cập nhật
    """
    try:
        success = await chat_session_service.update_session_metadata(session_id, metadata)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session không tồn tại: {session_id}"
            )
        
        logger.info(f"✅ Updated metadata for session: {session_id}")
        return {
            "message": "Metadata đã được cập nhật thành công",
            "session_id": session_id,
            "metadata": metadata,
            "updated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating metadata for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi cập nhật metadata: {str(e)}"
        )
