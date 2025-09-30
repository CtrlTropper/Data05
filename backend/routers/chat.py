"""
Chat router
Router xử lý truy vấn chatbot dựa trên RAG
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import logging
import json
import asyncio

# Import services
from services.embedding_service import embedding_service
from services.llm_service import llm_service
from services.security_filter import security_filter
from services.chat_session_service import chat_session_service
from services.rag_service import rag_service
from db.faiss_store import faiss_store

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatMessage(BaseModel):
    """Model cho chat message"""
    role: str  # "user" hoặc "assistant"
    content: str
    timestamp: str

class ChatRequest(BaseModel):
    """Request model cho chat"""
    question: str
    doc_id: Optional[str] = None  # Nếu None thì search toàn bộ
    category: Optional[str] = None  # Category để filter (Luat, TaiLieuTiengViet, TaiLieuTiengAnh, Uploads)
    session_id: Optional[str] = None  # ID của chat session
    max_tokens: int = 1000
    temperature: float = 0.7
    top_k: int = 5  # Số chunks liên quan nhất
    memory_limit: int = 5  # Số tin nhắn gần nhất để lấy từ lịch sử

class ChatResponse(BaseModel):
    """Response model cho chat"""
    response: str
    sources: List[Dict[str, Any]]  # Các chunks được sử dụng
    processing_time: float
    question: str
    doc_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatHistoryRequest(BaseModel):
    """Request model cho chat history"""
    session_id: str
    limit: int = 50

class ChatHistoryResponse(BaseModel):
    """Response model cho chat history"""
    messages: List[ChatMessage]
    session_id: str
    total: int

def create_context_from_sources(sources: List[Dict[str, Any]]) -> str:
    """
    Tạo context từ các sources
    
    Args:
        sources: Danh sách các chunks từ search
        
    Returns:
        str: Context được format
    """
    if not sources:
        return ""
    
    context_parts = []
    for i, source in enumerate(sources, 1):
        content = source.get("content", "")
        filename = source.get("filename", "Unknown")
        chunk_index = source.get("chunk_index", 0)
        
        context_parts.append(
            f"[{i}] {content}\n"
            f"    (Nguồn: {filename}, đoạn {chunk_index + 1})"
        )
    
    return "\n\n".join(context_parts)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat với hệ thống RAG - Chỉ hỗ trợ câu hỏi về An ninh An toàn thông tin
    """
    try:
        start_time = time.time()
        
        if not request.question or not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Câu hỏi không được để trống"
            )
        
        question = request.question.strip()
        
        # Step 0: Kiểm tra câu hỏi có liên quan đến ATTT không
        logger.info(f"🔒 Checking security relevance...")
        if not security_filter.is_security_related(question):
            logger.info(f"❌ Question not related to security: {question[:50]}...")
            return ChatResponse(
                response="Xin lỗi, tôi chỉ hỗ trợ các câu hỏi liên quan đến An ninh An toàn thông tin.",
                sources=[],
                processing_time=time.time() - start_time,
                question=question,
                doc_id=request.doc_id
            )
        
        logger.info(f"✅ Question is security-related: {question[:50]}...")
        
        # Step 0.5: Save user message to session if session_id provided
        if request.session_id:
            await chat_session_service.add_message(
                session_id=request.session_id,
                role="user",
                content=question
            )
            logger.info(f"💾 Saved user message to session: {request.session_id}")
        
        # Step 1: Search relevant chunks
        logger.info(f"🔍 Searching for relevant chunks...")
        search_results = faiss_store.search_text(
            query_text=question,
            top_k=request.top_k,
            doc_id=request.doc_id,
            category=request.category,
            embedding_service=embedding_service
        )
        
        if not search_results:
            logger.warning("⚠️ No relevant chunks found")
            # Generate answer without context
            response = llm_service.generate_answer(question, "")
            sources = []
        else:
            # Step 2: Create context from chunks
            logger.info(f"📝 Creating context from {len(search_results)} chunks...")
            retrieved_context = create_context_from_sources(search_results)
            
            # Step 3: Build context with memory (conversation history)
            logger.info(f"🧠 Building context with memory (limit: {request.memory_limit})...")
            full_context = await rag_service.build_context_with_memory(
                session_id=request.session_id,
                query=question,
                retrieved_context=retrieved_context,
                memory_limit=request.memory_limit
            )
            
            # Step 4: Generate answer with full context (including memory)
            logger.info("🤖 Generating answer with LLM and memory...")
            response = llm_service.generate_answer(question, full_context)
            
            # Step 5: Format sources
            sources = []
            for result in search_results:
                source = {
                    "content": result.get("content", "")[:200] + "...",  # Preview
                    "similarity_score": result.get("similarity_score", 0.0),
                    "document_id": result.get("document_id", ""),
                    "chunk_id": result.get("chunk_id", ""),
                    "filename": result.get("filename", ""),
                    "chunk_index": result.get("chunk_index", 0)
                }
                sources.append(source)
        
        processing_time = time.time() - start_time
        
        # Step 5: Save assistant response to session if session_id provided
        if request.session_id:
            await chat_session_service.add_message(
                session_id=request.session_id,
                role="assistant",
                content=response
            )
            logger.info(f"💾 Saved assistant response to session: {request.session_id}")
        
        logger.info(f"✅ Chat completed in {processing_time:.3f}s")
        
        return ChatResponse(
            response=response,
            sources=sources,
            processing_time=processing_time,
            question=question,
            doc_id=request.doc_id,
            session_id=request.session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xử lý chat: {str(e)}"
        )

@router.post("/chat/document/{document_id}", response_model=ChatResponse)
async def chat_with_document(
    document_id: str,
    request: ChatRequest
) -> ChatResponse:
    """
    Chat tập trung vào một tài liệu cụ thể
    """
    try:
        # Set document_id in request
        request.doc_id = document_id
        
        # Use the main chat function
        return await chat(request)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in document chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi chat với tài liệu: {str(e)}"
        )

@router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """
    Chat với streaming response - Chỉ hỗ trợ câu hỏi về An ninh An toàn thông tin
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Câu hỏi không được để trống"
            )
        
        question = request.question.strip()
        
        # Step 0: Kiểm tra câu hỏi có liên quan đến ATTT không
        if not security_filter.is_security_related(question):
            logger.info(f"❌ Question not related to security: {question[:50]}...")
            
            async def generate_rejection_stream():
                rejection_message = "Xin lỗi, tôi chỉ hỗ trợ các câu hỏi liên quan đến An ninh An toàn thông tin."
                yield f"data: {json.dumps({'type': 'start', 'question': question, 'sources_count': 0})}\n\n"
                
                # Stream rejection message word by word
                words = rejection_message.split()
                for word in words:
                    yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
                    await asyncio.sleep(0.1)  # Small delay for streaming effect
                
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
            
            return StreamingResponse(
                generate_rejection_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        logger.info(f"✅ Question is security-related: {question[:50]}...")
        
        # Step 0.5: Save user message to session if session_id provided
        if request.session_id:
            await chat_session_service.add_message(
                session_id=request.session_id,
                role="user",
                content=question
            )
            logger.info(f"💾 Saved user message to session: {request.session_id}")
        
        # Step 1: Search relevant chunks
        search_results = faiss_store.search_text(
            query_text=question,
            top_k=request.top_k,
            doc_id=request.doc_id,
            category=request.category,
            embedding_service=embedding_service
        )
        
        # Step 2: Create context from chunks
        retrieved_context = create_context_from_sources(search_results) if search_results else ""
        
        # Step 3: Build context with memory (conversation history)
        full_context = await rag_service.build_context_with_memory(
            session_id=request.session_id,
            query=question,
            retrieved_context=retrieved_context,
            memory_limit=request.memory_limit
        )
        
        # Step 3: Stream response
        async def generate_stream():
            try:
                # Send initial metadata
                yield f"data: {json.dumps({'type': 'start', 'question': question, 'sources_count': len(search_results)})}\n\n"
                
                # Stream response tokens
                full_response = ""
                for token in llm_service.generate_answer_with_streaming(question, full_context):
                    full_response += token
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                
                # Save assistant response to session if session_id provided
                if request.session_id:
                    await chat_session_service.add_message(
                        session_id=request.session_id,
                        role="assistant",
                        content=full_response
                    )
                    logger.info(f"💾 Saved assistant response to session: {request.session_id}")
                
                # Send completion signal
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
            except Exception as e:
                logger.error(f"❌ Error in streaming: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in stream chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi stream chat: {str(e)}"
        )

@router.get("/chat/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = 50
) -> ChatHistoryResponse:
    """
    Lấy lịch sử chat của một session
    """
    # TODO: Implement chat history logic
    # - Query chat history from database
    # - Apply limit
    # - Return message list
    
    return ChatHistoryResponse(
        messages=[],
        session_id=session_id,
        total=0
    )

@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Xóa lịch sử chat của một session
    """
    # TODO: Implement clear history logic
    # - Delete chat history from database
    
    return {"message": "Chat history cleared successfully"}

@router.get("/chat/sessions")
async def get_chat_sessions():
    """
    Lấy danh sách các chat sessions
    """
    # TODO: Implement get sessions logic
    # - Query active sessions
    # - Return session list with metadata
    
    return {"sessions": []}

@router.get("/chat/stats")
async def get_chat_stats():
    """
    Lấy thống kê về chat system
    """
    try:
        # Get LLM service info
        llm_info = llm_service.get_model_info()
        
        # Get embedding service info
        embedding_info = embedding_service.get_model_info()
        
        # Get FAISS stats
        faiss_stats = faiss_store.get_stats()
        
        # Get security filter stats
        security_filter_stats = security_filter.get_filter_stats()
        
        stats = {
            "llm_service": llm_info,
            "embedding_service": embedding_info,
            "faiss_store": faiss_stats,
            "security_filter": security_filter_stats,
            "chat_capabilities": {
                "text_chat": True,
                "document_chat": True,
                "streaming_chat": True,
                "rag_enabled": True,
                "security_filtered": True,
                "security_domains": security_filter_stats["security_domains"]
            }
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting chat stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy thống kê chat: {str(e)}"
        )
