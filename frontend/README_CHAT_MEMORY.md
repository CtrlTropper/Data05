# Frontend Chat Memory - Giao Diện Chat với Trí Nhớ Hội Thoại

Frontend ReactJS cho chatbot RAG + LLM với hỗ trợ nhiều đoạn chat và trí nhớ hội thoại, giao diện giống ChatGPT.

## 🎯 **TỔNG QUAN**

Frontend cung cấp:
- ✅ **Chat Sidebar**: Quản lý nhiều đoạn chat
- ✅ **Chat Area**: Hiển thị hội thoại với trí nhớ
- ✅ **Chat Input**: Nhập tin nhắn với auto-resize
- ✅ **Chat Message**: Hiển thị tin nhắn user/bot
- ✅ **Streaming Support**: Hỗ trợ streaming response
- ✅ **Memory Integration**: Tích hợp trí nhớ hội thoại

## 🏗️ **KIẾN TRÚC COMPONENT**

```
ChatPage
├── ChatSidebar
│   ├── Session List
│   ├── Create New Session
│   └── Delete Session
└── ChatArea
    ├── Chat Messages
    │   └── ChatMessage (User/Bot)
    └── ChatInput
        ├── Textarea (Auto-resize)
        └── Send Button
```

## 🔧 **COMPONENTS**

### **1. ChatPage** (`pages/ChatPage.jsx`)
- **Chức năng**: Component chính quản lý toàn bộ chat interface
- **State**: `currentSessionId`, `sessions`
- **Props**: Không có
- **Features**:
  - Load sessions từ backend
  - Auto-select session đầu tiên
  - Handle session selection
  - Handle new session creation
  - Handle session updates

### **2. ChatSidebar** (`components/ChatSidebar.jsx`)
- **Chức năng**: Sidebar quản lý các đoạn chat
- **Props**: `currentSessionId`, `onSessionSelect`, `onNewSession`, `className`
- **Features**:
  - Hiển thị danh sách sessions
  - Tạo session mới
  - Xóa session
  - Format session title và timestamp
  - Loading states

### **3. ChatArea** (`components/ChatArea.jsx`)
- **Chức năng**: Khu vực hiển thị hội thoại và input
- **Props**: `sessionId`, `onSessionUpdate`, `className`
- **Features**:
  - Load messages từ session
  - Send message với streaming
  - Auto-scroll to bottom
  - Error handling
  - Cancel streaming

### **4. ChatMessage** (`components/ChatMessage.jsx`)
- **Chức năng**: Hiển thị tin nhắn user/bot
- **Props**: `message`, `isStreaming`
- **Features**:
  - Format timestamp
  - Copy to clipboard
  - Streaming indicator
  - User/Bot styling

### **5. ChatInput** (`components/ChatInput.jsx`)
- **Chức năng**: Input box để nhập tin nhắn
- **Props**: `onSendMessage`, `disabled`, `placeholder`, `className`
- **Features**:
  - Auto-resize textarea
  - Enter/Shift+Enter handling
  - Character count
  - Loading state

## 📊 **TÍNH NĂNG CHÍNH**

### **1. Session Management**
- ✅ **Create Session**: Tạo đoạn chat mới
- ✅ **List Sessions**: Hiển thị danh sách sessions
- ✅ **Select Session**: Chọn session để chat
- ✅ **Delete Session**: Xóa session
- ✅ **Auto-select**: Tự động chọn session đầu tiên

### **2. Message Display**
- ✅ **User Messages**: Tin nhắn user (bên phải, màu xanh)
- ✅ **Bot Messages**: Tin nhắn bot (bên trái, màu trắng)
- ✅ **Timestamp**: Hiển thị thời gian
- ✅ **Copy Function**: Copy tin nhắn bot
- ✅ **Streaming Indicator**: Hiển thị đang streaming

### **3. Input Features**
- ✅ **Auto-resize**: Textarea tự động resize
- ✅ **Enter Handling**: Enter gửi, Shift+Enter xuống dòng
- ✅ **Character Count**: Đếm ký tự
- ✅ **Loading State**: Disable khi đang gửi
- ✅ **Placeholder**: Text hướng dẫn

### **4. Streaming Support**
- ✅ **Real-time**: Hiển thị response real-time
- ✅ **Cancel**: Hủy streaming
- ✅ **Error Handling**: Xử lý lỗi streaming
- ✅ **Full Response**: Lưu response đầy đủ

### **5. Memory Integration**
- ✅ **Session-based**: Trí nhớ theo session
- ✅ **Auto-load**: Tự động load lịch sử
- ✅ **Context Awareness**: Hiểu ngữ cảnh hội thoại
- ✅ **Reference Resolution**: Giải quyết tham chiếu

## 🎨 **UI/UX DESIGN**

### **Layout**
```
┌─────────────────────────────────────────────────────────┐
│                    Chat Header                          │
├─────────────┬───────────────────────────────────────────┤
│             │                                           │
│   Sidebar   │              Chat Area                    │
│             │                                           │
│  - Sessions │  - Messages (User/Bot)                    │
│  - Create   │  - Streaming                              │
│  - Delete   │  - Auto-scroll                            │
│             │                                           │
├─────────────┼───────────────────────────────────────────┤
│             │              Input Area                   │
│             │  - Textarea (Auto-resize)                 │
│             │  - Send Button                            │
│             │  - Helper Text                            │
└─────────────┴───────────────────────────────────────────┘
```

### **Color Scheme**
- **Primary**: Blue (#3B82F6)
- **User Messages**: Blue background
- **Bot Messages**: White/Gray background
- **Sidebar**: Gray background
- **Input**: White background with border

### **Responsive Design**
- **Desktop**: Sidebar 320px, Chat area flexible
- **Mobile**: Collapsible sidebar
- **Tablet**: Adaptive layout

## 🔌 **API INTEGRATION**

### **Chat Sessions API**
```javascript
// Create session
const response = await chatSessionsAPI.create(title, metadata);

// Get all sessions
const response = await chatSessionsAPI.getAll();

// Get session messages
const response = await chatSessionsAPI.getMessages(sessionId, limit);

// Delete session
await chatSessionsAPI.delete(sessionId);
```

### **Chat API**
```javascript
// Send message
const response = await chatAPI.chat(question, {
  session_id: sessionId,
  top_k: 5,
  memory_limit: 5
});

// Streaming chat
const response = await chatAPI.streamChat(question, {
  session_id: sessionId,
  top_k: 5,
  memory_limit: 5
});
```

## 🧪 **TESTING**

### **Test Scenarios**
1. **Session Management**
   - Tạo session mới
   - Chọn session
   - Xóa session
   - Auto-select session

2. **Message Flow**
   - Gửi tin nhắn user
   - Nhận response bot
   - Streaming response
   - Copy message

3. **Memory Integration**
   - Hội thoại liên tục
   - Tham chiếu ngữ cảnh
   - Load lịch sử

4. **Error Handling**
   - Network errors
   - API errors
   - Streaming errors

### **Test Commands**
```bash
# Start frontend
npm run dev

# Test in browser
http://localhost:3000

# Test with backend
# Make sure backend is running on port 8000
```

## 📱 **RESPONSIVE DESIGN**

### **Breakpoints**
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### **Mobile Features**
- Collapsible sidebar
- Touch-friendly buttons
- Optimized input
- Swipe gestures

## 🚀 **DEPLOYMENT**

### **Build Commands**
```bash
# Install dependencies
npm install

# Development
npm run dev

# Production build
npm run build

# Preview build
npm run preview
```

### **Docker Deployment**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 🔧 **CONFIGURATION**

### **Environment Variables**
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=RAG Chatbot
VITE_APP_VERSION=1.0.0
```

### **API Configuration**
```javascript
// services/api.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
```

## 🎯 **USE CASES**

### **1. Multi-Session Chat**
- Người dùng có thể tạo nhiều đoạn chat
- Mỗi session có lịch sử riêng
- Chuyển đổi giữa các session

### **2. Context-Aware Conversations**
- Chatbot nhớ ngữ cảnh hội thoại
- Hiểu tham chiếu ("nó", "cái đó")
- Duy trì tính liên tục

### **3. Streaming Responses**
- Hiển thị response real-time
- Cải thiện trải nghiệm người dùng
- Hủy streaming khi cần

### **4. Message Management**
- Copy tin nhắn bot
- Timestamp cho mỗi tin nhắn
- Auto-scroll to bottom

## 🎉 **KẾT LUẬN**

Frontend đã hoàn thiện với:

- ✅ **Chat Sidebar**: Quản lý nhiều đoạn chat
- ✅ **Chat Area**: Hiển thị hội thoại với trí nhớ
- ✅ **Chat Input**: Nhập tin nhắn với auto-resize
- ✅ **Chat Message**: Hiển thị tin nhắn user/bot
- ✅ **Streaming Support**: Hỗ trợ streaming response
- ✅ **Memory Integration**: Tích hợp trí nhớ hội thoại
- ✅ **Responsive Design**: Giao diện responsive
- ✅ **Error Handling**: Xử lý lỗi toàn diện

Giao diện chat giờ đây giống ChatGPT với trí nhớ hội thoại!
