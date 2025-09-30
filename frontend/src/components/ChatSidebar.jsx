import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  MessageSquare, 
  Trash2, 
  MoreVertical,
  Loader2
} from 'lucide-react';
import { chatSessionsAPI } from '../services/api';

const ChatSidebar = ({ 
  currentSessionId, 
  onSessionSelect, 
  onNewSession,
  className = "" 
}) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [deleting, setDeleting] = useState(null);

  // Load sessions on component mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const response = await chatSessionsAPI.getAll();
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Error loading sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = async () => {
    try {
      setCreating(true);
      const response = await chatSessionsAPI.create(`Chat ${new Date().toLocaleString()}`);
      
      const newSession = response.data;
      setSessions(prev => [newSession, ...prev]);
      onNewSession(newSession.session_id);
    } catch (error) {
      console.error('Error creating session:', error);
    } finally {
      setCreating(false);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa đoạn chat này?')) {
      return;
    }

    try {
      setDeleting(sessionId);
      await chatSessionsAPI.delete(sessionId);
      
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
      
      // If deleted session was current, create a new one
      if (currentSessionId === sessionId) {
        createNewSession();
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    } finally {
      setDeleting(null);
    }
  };

  const formatSessionTitle = (session) => {
    if (session.title && !session.title.startsWith('Chat Session')) {
      return session.title;
    }
    return `Chat ${session.session_id.slice(0, 8)}...`;
  };

  const formatLastUpdated = (updatedAt) => {
    const date = new Date(updatedAt);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Vừa xong';
    if (diffMins < 60) return `${diffMins} phút trước`;
    if (diffHours < 24) return `${diffHours} giờ trước`;
    if (diffDays < 7) return `${diffDays} ngày trước`;
    return date.toLocaleDateString();
  };

  return (
    <div className={`bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={createNewSession}
          disabled={creating}
          className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {creating ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Đang tạo...
            </>
          ) : (
            <>
              <Plus className="w-4 h-4 mr-2" />
              Tạo đoạn chat mới
            </>
          )}
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
          </div>
        ) : sessions.length === 0 ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Chưa có đoạn chat nào</p>
            <p className="text-sm">Tạo đoạn chat mới để bắt đầu</p>
          </div>
        ) : (
          <div className="p-2">
            {sessions.map((session) => (
              <div
                key={session.session_id}
                className={`group relative mb-2 p-3 rounded-lg cursor-pointer transition-colors ${
                  currentSessionId === session.session_id
                    ? 'bg-blue-100 dark:bg-blue-900 border border-blue-200 dark:border-blue-700'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
                onClick={() => onSessionSelect(session.session_id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {formatSessionTitle(session)}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {session.message_count || 0} tin nhắn • {formatLastUpdated(session.updated_at)}
                    </p>
                  </div>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.session_id);
                    }}
                    disabled={deleting === session.session_id}
                    className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-all"
                  >
                    {deleting === session.session_id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          {sessions.length} đoạn chat
        </div>
      </div>
    </div>
  );
};

export default ChatSidebar;