import React, { useState, useEffect } from 'react';
import ChatSidebar from '../components/ChatSidebar';
import ChatArea from '../components/ChatArea';

const ChatPage = () => {
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);

  // Load sessions on component mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/chat_sessions');
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
        
        // Auto-select first session if available
        if (data.sessions && data.sessions.length > 0 && !currentSessionId) {
          setCurrentSessionId(data.sessions[0].session_id);
        }
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const handleSessionSelect = (sessionId) => {
    setCurrentSessionId(sessionId);
  };

  const handleNewSession = (sessionId) => {
    setCurrentSessionId(sessionId);
    loadSessions(); // Refresh sessions list
  };

  const handleSessionUpdate = () => {
    loadSessions(); // Refresh sessions list when messages are added
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Chat Sidebar */}
      <div className="w-80 flex-shrink-0">
        <ChatSidebar
          currentSessionId={currentSessionId}
          onSessionSelect={handleSessionSelect}
          onNewSession={handleNewSession}
          className="h-full"
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              RAG Chatbot với Trí Nhớ Hội Thoại
            </h1>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {currentSessionId ? `Session: ${currentSessionId.slice(0, 8)}...` : 'Chưa chọn session'}
            </div>
          </div>
        </div>

        {/* Chat Messages and Input */}
        <div className="flex-1">
          <ChatArea
            sessionId={currentSessionId}
            onSessionUpdate={handleSessionUpdate}
            className="h-full"
          />
        </div>
      </div>
    </div>
  );
};

export default ChatPage;