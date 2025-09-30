"""
RAG Service
Xử lý logic RAG (Retrieval-Augmented Generation) với trí nhớ hội thoại
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RAGService:
    """Service xử lý RAG với trí nhớ hội thoại"""
    
    def __init__(self):
        self.vector_db = None  # Will be injected
        self.model_manager = None  # Will be injected
        self.chat_session_service = None  # Will be injected
    
    async def search_relevant_chunks(
        self, 
        query: str, 
        document_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm các chunks liên quan đến query
        """
        try:
            # TODO: Implement search logic
            # 1. Generate embedding for query
            # 2. Search in FAISS index
            # 3. Filter by document_id if specified
            # 4. Return top_k results with metadata
            
            # Placeholder search results
            results = [
                {
                    "chunk_id": "chunk_1",
                    "content": "Sample chunk content 1",
                    "document_id": "doc_1",
                    "similarity_score": 0.95,
                    "page_number": 1
                },
                {
                    "chunk_id": "chunk_2", 
                    "content": "Sample chunk content 2",
                    "document_id": "doc_1",
                    "similarity_score": 0.87,
                    "page_number": 2
                }
            ]
            
            # Filter by document_id if specified
            if document_id:
                results = [r for r in results if r["document_id"] == document_id]
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Error searching chunks: {e}")
            raise
    
    async def create_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Tạo context từ các chunks
        """
        try:
            if not chunks:
                return ""
            
            # TODO: Implement context creation
            # 1. Sort chunks by similarity score
            # 2. Combine content with metadata
            # 3. Format for LLM input
            
            context_parts = []
            for i, chunk in enumerate(chunks, 1):
                context_parts.append(
                    f"[{i}] {chunk['content']}\n"
                    f"Source: Document {chunk['document_id']}, Page {chunk.get('page_number', 'N/A')}\n"
                )
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Error creating context: {e}")
            raise
    
    async def generate_rag_response(
        self,
        query: str,
        context: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate response sử dụng RAG
        """
        try:
            start_time = datetime.now()
            
            # TODO: Implement RAG response generation
            # 1. Create prompt with context
            # 2. Generate response using LLM
            # 3. Return response with metadata
            
            # Create prompt
            prompt = f"""
Context:
{context}

Question: {query}

Answer based on the context above:
"""
            
            # Generate response (placeholder)
            response = "Đây là câu trả lời dựa trên RAG (placeholder)."
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            metadata = {
                "processing_time": processing_time,
                "context_length": len(context),
                "tokens_used": 0,  # Placeholder
                "model_used": "gpt-oss-20b"
            }
            
            return response, metadata
            
        except Exception as e:
            logger.error(f"❌ Error generating RAG response: {e}")
            raise
    
    async def chat_with_rag(
        self,
        query: str,
        document_id: Optional[str] = None,
        top_k: int = 5,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Chat với RAG - main function
        """
        try:
            # 1. Search relevant chunks
            chunks = await self.search_relevant_chunks(
                query=query,
                document_id=document_id,
                top_k=top_k
            )
            
            # 2. Create context
            context = await self.create_context(chunks)
            
            # 3. Generate response
            response, metadata = await self.generate_rag_response(
                query=query,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # 4. Prepare sources
            sources = [
                {
                    "chunk_id": chunk["chunk_id"],
                    "content": chunk["content"][:200] + "...",  # Preview
                    "document_id": chunk["document_id"],
                    "similarity_score": chunk["similarity_score"],
                    "page_number": chunk.get("page_number")
                }
                for chunk in chunks
            ]
            
            return {
                "response": response,
                "sources": sources,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Error in chat_with_rag: {e}")
            raise

    async def build_context_with_memory(
        self,
        session_id: Optional[str],
        query: str,
        retrieved_context: str,
        memory_limit: int = 5
    ) -> str:
        """
        Xây dựng context với trí nhớ hội thoại
        
        Args:
            session_id: ID của chat session
            query: Câu hỏi hiện tại
            retrieved_context: Context từ vector search
            memory_limit: Số tin nhắn gần nhất để lấy từ lịch sử
            
        Returns:
            str: Context hoàn chỉnh bao gồm lịch sử hội thoại
        """
        try:
            context_parts = []
            
            # 1. Lấy lịch sử hội thoại nếu có session_id
            if session_id and self.chat_session_service:
                logger.info(f"🧠 Building context with memory for session: {session_id}")
                
                # Lấy tin nhắn gần nhất từ session
                messages = await self.chat_session_service.get_session_messages(
                    session_id=session_id,
                    limit=memory_limit
                )
                
                if messages and len(messages) > 0:
                    # Tạo context từ lịch sử hội thoại
                    conversation_context = self._format_conversation_history(messages)
                    context_parts.append(conversation_context)
                    logger.info(f"📚 Added {len(messages)} messages from conversation history")
                else:
                    logger.info("📚 No conversation history found")
            else:
                logger.info("📚 No session_id provided, skipping conversation history")
            
            # 2. Thêm context từ vector search
            if retrieved_context and retrieved_context.strip():
                context_parts.append("THÔNG TIN THAM KHẢO:")
                context_parts.append(retrieved_context.strip())
                logger.info("📖 Added retrieved context from vector search")
            
            # 3. Ghép tất cả context lại
            full_context = "\n\n".join(context_parts)
            
            logger.info(f"✅ Built context with memory. Total length: {len(full_context)} chars")
            return full_context
            
        except Exception as e:
            logger.error(f"❌ Error building context with memory: {e}")
            # Fallback to retrieved context only
            return retrieved_context or ""

    def _format_conversation_history(self, messages: List[Dict[str, Any]]) -> str:
        """
        Format lịch sử hội thoại thành context
        
        Args:
            messages: Danh sách tin nhắn từ session
            
        Returns:
            str: Context được format từ lịch sử hội thoại
        """
        try:
            if not messages:
                return ""
            
            # Lọc chỉ lấy tin nhắn user và assistant
            filtered_messages = [
                msg for msg in messages 
                if msg.get("role") in ["user", "assistant"]
            ]
            
            if not filtered_messages:
                return ""
            
            # Format conversation history
            conversation_parts = ["LỊCH SỬ HỘI THOẠI:"]
            
            for msg in filtered_messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                if role == "user":
                    conversation_parts.append(f"Người dùng: {content}")
                elif role == "assistant":
                    conversation_parts.append(f"Trợ lý: {content}")
            
            return "\n".join(conversation_parts)
            
        except Exception as e:
            logger.error(f"❌ Error formatting conversation history: {e}")
            return ""

    async def chat_with_memory(
        self,
        query: str,
        session_id: Optional[str] = None,
        document_id: Optional[str] = None,
        top_k: int = 5,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        memory_limit: int = 5
    ) -> Dict[str, Any]:
        """
        Chat với RAG và trí nhớ hội thoại
        
        Args:
            query: Câu hỏi của user
            session_id: ID của chat session
            document_id: ID của document (optional)
            top_k: Số chunks tối đa từ vector search
            max_tokens: Số token tối đa cho response
            temperature: Temperature cho generation
            memory_limit: Số tin nhắn gần nhất để lấy từ lịch sử
            
        Returns:
            Dict[str, Any]: Response với metadata
        """
        try:
            logger.info(f"🧠 Starting chat with memory for session: {session_id}")
            
            # 1. Search relevant chunks từ vector DB
            chunks = await self.search_relevant_chunks(
                query=query,
                document_id=document_id,
                top_k=top_k
            )
            
            # 2. Tạo context từ vector search
            retrieved_context = await self.create_context(chunks)
            
            # 3. Xây dựng context với trí nhớ hội thoại
            full_context = await self.build_context_with_memory(
                session_id=session_id,
                query=query,
                retrieved_context=retrieved_context,
                memory_limit=memory_limit
            )
            
            # 4. Generate response với context đầy đủ
            response, metadata = await self.generate_rag_response(
                query=query,
                context=full_context,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # 5. Prepare sources
            sources = [
                {
                    "chunk_id": chunk.get("chunk_id", ""),
                    "content": chunk.get("content", "")[:200] + "...",
                    "document_id": chunk.get("document_id", ""),
                    "similarity_score": chunk.get("similarity_score", 0.0),
                    "page_number": chunk.get("page_number")
                }
                for chunk in chunks
            ]
            
            # 6. Thêm metadata về memory
            metadata.update({
                "has_memory": session_id is not None,
                "memory_limit": memory_limit,
                "context_with_memory": True
            })
            
            logger.info(f"✅ Chat with memory completed for session: {session_id}")
            
            return {
                "response": response,
                "sources": sources,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Error in chat_with_memory: {e}")
            raise

# Global RAG service instance
rag_service = RAGService()
