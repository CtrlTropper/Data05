import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Loader2, AlertCircle } from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { chatAPI, chatSessionsAPI } from '../services/api';

const ChatArea = ({ 
  sessionId, 
  onSessionUpdate,
  className = "" 
}) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [streamingMessage, setStreamingMessage] = useState(null);
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Load messages when session changes
  useEffect(() => {
    if (sessionId) {
      loadMessages();
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadMessages = async () => {
    if (!sessionId) return;

    try {
      setLoading(true);
      setError(null);
      const response = await chatSessionsAPI.getMessages(sessionId);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error loading messages:', error);
      setError('Không thể tải lịch sử hội thoại');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (messageText) => {
    if (!sessionId || !messageText.trim()) return;

    try {
      setSending(true);
      setError(null);

      // Add user message immediately
      const userMessage = {
        role: 'user',
        content: messageText,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);

      // Send to backend
      const response = await chatAPI.chat(messageText, {
        session_id: sessionId,
        top_k: 5,
        memory_limit: 5
      });

      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Notify parent of session update
      if (onSessionUpdate) {
        onSessionUpdate();
      }

    } catch (error) {
      console.error('Error sending message:', error);
      setError('Không thể gửi tin nhắn. Vui lòng thử lại.');
      
      // Remove the user message if sending failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setSending(false);
    }
  };

  const sendStreamingMessage = async (messageText) => {
    if (!sessionId || !messageText.trim()) return;

    try {
      setSending(true);
      setError(null);

      // Add user message immediately
      const userMessage = {
        role: 'user',
        content: messageText,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);

      // Create abort controller for cancellation
      abortControllerRef.current = new AbortController();

      // Start streaming
      const response = await chatAPI.streamChat(messageText, {
        session_id: sessionId,
        top_k: 5,
        memory_limit: 5
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      // Initialize streaming message
      setStreamingMessage({
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString()
      });

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'token') {
                  fullResponse += data.content;
                  setStreamingMessage(prev => ({
                    ...prev,
                    content: fullResponse
                  }));
                } else if (data.type === 'end') {
                  // Add final message to messages list
                  const assistantMessage = {
                    role: 'assistant',
                    content: fullResponse,
                    timestamp: new Date().toISOString()
                  };
                  setMessages(prev => [...prev, assistantMessage]);
                  setStreamingMessage(null);

                  // Notify parent of session update
                  if (onSessionUpdate) {
                    onSessionUpdate();
                  }
                } else if (data.type === 'error') {
                  throw new Error(data.message || 'Streaming error');
                }
              } catch (parseError) {
                console.error('Error parsing streaming data:', parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Streaming cancelled');
      } else {
        console.error('Error in streaming:', error);
        setError('Không thể gửi tin nhắn. Vui lòng thử lại.');
        
        // Remove the user message if sending failed
        setMessages(prev => prev.slice(0, -1));
      }
      
      setStreamingMessage(null);
    } finally {
      setSending(false);
      abortControllerRef.current = null;
    }
  };

  const handleSendMessage = (messageText) => {
    // Use streaming by default
    sendStreamingMessage(messageText);
  };

  const cancelStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  if (!sessionId) {
    return (
      <div className={`flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400 ${className}`}>
        <MessageSquare className="w-16 h-16 mb-4 opacity-50" />
        <h3 className="text-lg font-medium mb-2">Chọn một đoạn chat</h3>
        <p className="text-sm text-center">
          Chọn một đoạn chat từ sidebar để bắt đầu hội thoại
        </p>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <p className="text-red-600 dark:text-red-400 mb-2">{error}</p>
              <button
                onClick={loadMessages}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Thử lại
              </button>
            </div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Bắt đầu hội thoại
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                Gửi tin nhắn đầu tiên để bắt đầu trò chuyện
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage
                key={`${message.timestamp}-${index}`}
                message={message}
              />
            ))}
            
            {/* Streaming Message */}
            {streamingMessage && (
              <ChatMessage
                message={streamingMessage}
                isStreaming={true}
              />
            )}
            
            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={sending}
        placeholder={sending ? "Đang gửi..." : "Nhập câu hỏi của bạn..."}
      />

      {/* Cancel streaming button */}
      {sending && streamingMessage && (
        <div className="p-2 bg-yellow-50 dark:bg-yellow-900 border-t border-yellow-200 dark:border-yellow-700">
          <button
            onClick={cancelStreaming}
            className="w-full px-4 py-2 text-sm text-yellow-800 dark:text-yellow-200 hover:bg-yellow-100 dark:hover:bg-yellow-800 rounded"
          >
            Hủy gửi tin nhắn
          </button>
        </div>
      )}
    </div>
  );
};

export default ChatArea;