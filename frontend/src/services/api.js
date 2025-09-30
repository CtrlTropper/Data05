import axios from 'axios';

// Base API configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    
    // Handle common errors
    if (error.response?.status === 500) {
      console.error('Server error - check backend logs');
    } else if (error.code === 'ECONNREFUSED') {
      console.error('Cannot connect to backend - make sure it\'s running on port 8000');
    }
    
    return Promise.reject(error);
  }
);

// Health Check API
export const healthAPI = {
  check: () => api.get('/health'),
};

// Documents API
export const documentsAPI = {
  // Upload document
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Get all documents
  getAll: () => api.get('/documents'),

  // Get document by ID
  getById: (id) => api.get(`/documents/${id}`),

  // Delete document
  delete: (id) => api.delete(`/documents/${id}`),

  // Select document
  select: (id) => api.post(`/documents/${id}/select`),
};

// Embedding API
export const embeddingAPI = {
  // Embed document
  embedDocument: (docId, options = {}) => 
    api.post(`/embed/document/${docId}`, {
      chunk_size: 500,
      chunk_overlap: 50,
      ...options,
    }),

  // Embed text
  embedText: (text) => 
    api.post('/embed/text', { text }),

  // Get embedding stats
  getStats: () => api.get('/embed/stats'),
};

// Search API
export const searchAPI = {
  // Search by text
  searchText: (query, options = {}) => 
    api.post('/search/text', {
      query,
      top_k: 5,
      ...options,
    }),

  // Search by vector
  searchVector: (vector, options = {}) => 
    api.post('/search/vector', {
      vector,
      top_k: 5,
      ...options,
    }),

  // Get document contexts
  getDocumentContexts: (docId) => 
    api.get(`/search/document/${docId}`),

  // Get search stats
  getStats: () => api.get('/search/stats'),
};

// Chat API
export const chatAPI = {
  // Basic chat
  chat: (question, options = {}) => 
    api.post('/chat', {
      question,
      top_k: 5,
      max_tokens: 1000,
      temperature: 0.7,
      ...options,
    }),

  // Chat with specific document
  chatWithDocument: (docId, question, options = {}) => 
    api.post(`/chat/document/${docId}`, {
      question,
      top_k: 5,
      max_tokens: 1000,
      temperature: 0.7,
      ...options,
    }),

  // Streaming chat
  streamChat: (question, options = {}) => {
    return fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        top_k: 5,
        max_tokens: 1000,
        temperature: 0.7,
        ...options,
      }),
    });
  },

  // Get chat stats
  getStats: () => api.get('/chat/stats'),
};

// Chat Sessions API
export const chatSessionsAPI = {
  // Create new session
  create: (title, metadata = {}) => 
    api.post('/chat_sessions', { title, metadata }),

  // Get all sessions
  getAll: () => api.get('/chat_sessions'),

  // Get session by ID
  getById: (sessionId) => api.get(`/chat_sessions/${sessionId}`),

  // Delete session
  delete: (sessionId) => api.delete(`/chat_sessions/${sessionId}`),

  // Add message to session
  addMessage: (sessionId, role, content) => 
    api.post(`/chat_sessions/${sessionId}/messages`, { role, content }),

  // Get session messages
  getMessages: (sessionId, limit = 50) => 
    api.get(`/chat_sessions/${sessionId}/messages?limit=${limit}`),

  // Get session stats
  getStats: () => api.get('/chat_sessions/stats'),
};

// Utility functions
export const apiUtils = {
  // Check if backend is running
  isBackendRunning: async () => {
    try {
      await healthAPI.check();
      return true;
    } catch (error) {
      return false;
    }
  },

  // Get error message from API error
  getErrorMessage: (error) => {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return 'Có lỗi xảy ra';
  },

  // Format file size
  formatFileSize: (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  // Format date
  formatDate: (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN');
  },
};

export default api;
