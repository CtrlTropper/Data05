import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, AlertCircle } from 'lucide-react';

const ChatInput = ({ 
  onSendMessage, 
  disabled = false, 
  placeholder = "Nhập câu hỏi của bạn...",
  className = ""
}) => {
  const [message, setMessage] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleCompositionStart = () => {
    setIsComposing(true);
  };

  const handleCompositionEnd = () => {
    setIsComposing(false);
  };

  return (
    <div className={`border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 ${className}`}>
      <form onSubmit={handleSubmit} className="p-4">
        <div className="flex items-end space-x-3">
          {/* Input Area */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              onCompositionStart={handleCompositionStart}
              onCompositionEnd={handleCompositionEnd}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
            
            {/* Character count */}
            {message.length > 0 && (
              <div className="absolute bottom-1 right-12 text-xs text-gray-400">
                {message.length}
              </div>
            )}
          </div>

          {/* Send Button */}
          <button
            type="submit"
            disabled={!message.trim() || disabled}
            className="flex-shrink-0 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {disabled ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Helper Text */}
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          Nhấn Enter để gửi, Shift + Enter để xuống dòng
        </div>
      </form>
    </div>
  );
};

export default ChatInput;