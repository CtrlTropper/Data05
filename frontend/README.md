# RAG + LLM Chatbot Frontend

Frontend ReactJS cho hệ thống chatbot RAG + LLM hoạt động offline.

## 🎯 **TỔNG QUAN**

Frontend được xây dựng với ReactJS, cung cấp giao diện người dùng cho hệ thống chatbot RAG + LLM offline với các tính năng:

- ✅ **Chat với AI**: Giao diện chat trực quan với RAG + LLM
- ✅ **Quản lý tài liệu**: Upload, xem, xóa, chọn tài liệu
- ✅ **Tích hợp backend**: Gọi API FastAPI backend
- ✅ **Responsive design**: Tương thích mobile và desktop
- ✅ **Dark/Light mode**: Chế độ sáng/tối

## 🚀 **CÀI ĐẶT VÀ CHẠY**

### **1. Cài đặt Dependencies**
```bash
cd frontend
npm install
```

### **2. Chạy Development Server**
```bash
npm run dev
```

Frontend sẽ chạy tại: http://localhost:3000

### **3. Build Production**
```bash
npm run build
```

## 📁 **CẤU TRÚC DỰ ÁN**

```
frontend/
├── public/                 # Static files
├── src/
│   ├── components/         # Reusable components
│   │   ├── Layout.jsx     # Main layout component
│   │   ├── LoadingSpinner.jsx
│   │   ├── Toast.jsx
│   │   └── FileUpload.jsx
│   ├── pages/             # Page components
│   │   ├── ChatPage.jsx   # Trang chat
│   │   └── DocumentsPage.jsx # Trang quản lý tài liệu
│   ├── services/          # API services
│   │   └── api.js         # API client
│   ├── App.jsx            # Main app component
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles
├── package.json
├── vite.config.js
└── README.md
```

## 🎨 **TÍNH NĂNG CHÍNH**

### **1. Trang Chatbot (`/`)**
- **Input câu hỏi**: Textarea với hỗ trợ Enter để gửi
- **Hiển thị câu trả lời**: Chat bubbles với timestamp
- **Chọn tài liệu**: Dropdown để chọn tài liệu cụ thể
- **Sources**: Hiển thị nguồn tham khảo từ RAG
- **Copy message**: Sao chép tin nhắn
- **Loading states**: Hiển thị trạng thái đang xử lý

### **2. Trang Quản lý Tài liệu (`/documents`)**
- **Upload file**: Drag & drop hoặc click để chọn
- **Danh sách tài liệu**: Hiển thị tất cả tài liệu đã upload
- **Xóa tài liệu**: Xóa tài liệu với xác nhận
- **Chọn tài liệu**: Chọn tài liệu để chat
- **Embedding status**: Trạng thái embedding của từng tài liệu
- **File info**: Thông tin chi tiết về file

### **3. Layout & Navigation**
- **Sidebar**: Navigation menu với các trang
- **Responsive**: Tự động thu gọn trên mobile
- **Dark/Light mode**: Chuyển đổi theme
- **Header**: Thông tin hệ thống

## 🔧 **API INTEGRATION**

### **API Endpoints được sử dụng:**

#### **Health Check**
- `GET /api/health` - Kiểm tra trạng thái backend

#### **Documents**
- `POST /api/documents/upload` - Upload tài liệu
- `GET /api/documents` - Lấy danh sách tài liệu
- `GET /api/documents/{id}` - Lấy thông tin tài liệu
- `DELETE /api/documents/{id}` - Xóa tài liệu
- `POST /api/documents/{id}/select` - Chọn tài liệu

#### **Embedding**
- `POST /api/embed/document/{id}` - Tạo embeddings cho tài liệu
- `GET /api/embed/stats` - Thống kê embedding

#### **Chat**
- `POST /api/chat` - Chat cơ bản
- `POST /api/chat/document/{id}` - Chat với tài liệu cụ thể
- `GET /api/chat/stats` - Thống kê chat

### **Error Handling**
- Interceptors cho request/response
- Hiển thị lỗi user-friendly
- Retry logic cho failed requests
- Connection status checking

## 🎨 **UI/UX FEATURES**

### **Design System**
- **Colors**: Consistent color palette với CSS variables
- **Typography**: System fonts với proper hierarchy
- **Spacing**: Consistent spacing scale
- **Components**: Reusable component library

### **Responsive Design**
- **Mobile-first**: Tối ưu cho mobile
- **Breakpoints**: sm, md, lg, xl
- **Flexible layouts**: Grid và Flexbox
- **Touch-friendly**: Buttons và interactions

### **Accessibility**
- **Keyboard navigation**: Tab, Enter, Escape
- **Screen readers**: Proper ARIA labels
- **Color contrast**: WCAG compliant
- **Focus management**: Visible focus indicators

## 🔄 **STATE MANAGEMENT**

### **Local State**
- React hooks (useState, useEffect)
- Component-level state
- Form state management

### **API State**
- Loading states
- Error handling
- Success feedback
- Data caching

## 📱 **RESPONSIVE BREAKPOINTS**

```css
/* Mobile */
@media (max-width: 640px) { }

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) { }

/* Desktop */
@media (min-width: 1025px) { }
```

## 🎯 **WORKFLOW SỬ DỤNG**

### **1. Upload và Embedding Tài liệu**
1. Vào trang "Quản lý Tài liệu"
2. Upload file PDF/TXT
3. Click "Embed" để tạo embeddings
4. Chọn tài liệu để chat

### **2. Chat với AI**
1. Vào trang "Chatbot"
2. Chọn tài liệu (optional)
3. Nhập câu hỏi
4. Nhận câu trả lời với sources

### **3. Quản lý Tài liệu**
1. Xem danh sách tài liệu
2. Xóa tài liệu không cần thiết
3. Chọn tài liệu để chat
4. Theo dõi trạng thái embedding

## 🛠 **DEVELOPMENT**

### **Scripts**
```bash
# Development
npm run dev

# Build
npm run build

# Preview build
npm run preview

# Lint
npm run lint
```

### **Dependencies**
- **React 18**: UI framework
- **React Router**: Routing
- **Axios**: HTTP client
- **Lucide React**: Icons
- **React Dropzone**: File upload
- **Vite**: Build tool

### **Environment Variables**
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## 🚀 **DEPLOYMENT**

### **Build for Production**
```bash
npm run build
```

### **Serve Static Files**
```bash
# Using serve
npx serve dist

# Using nginx
# Copy dist/ to nginx html directory
```

### **Docker**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

#### **1. Backend Connection Error**
```
Error: Cannot connect to backend
```
**Solution**: Đảm bảo backend FastAPI đang chạy trên port 8000

#### **2. CORS Error**
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy
```
**Solution**: Backend đã cấu hình CORS cho localhost:3000

#### **3. File Upload Error**
```
Error uploading file
```
**Solution**: Kiểm tra kích thước file (max 50MB) và định dạng (PDF/TXT)

### **Debug Mode**
```bash
# Enable debug logging
localStorage.setItem('debug', 'true')
```

## 📊 **PERFORMANCE**

### **Optimizations**
- **Code splitting**: Lazy loading components
- **Image optimization**: Proper image formats
- **Bundle analysis**: Vite bundle analyzer
- **Caching**: API response caching

### **Metrics**
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Time to Interactive**: < 3.5s

## 🎉 **KẾT LUẬN**

Frontend ReactJS đã được hoàn thiện với:

- ✅ **Giao diện hiện đại**: Clean, responsive design
- ✅ **Tích hợp backend**: API calls hoàn chỉnh
- ✅ **User experience**: Intuitive workflow
- ✅ **Error handling**: Robust error management
- ✅ **Performance**: Optimized loading và rendering

Hệ thống sẵn sàng sử dụng với backend FastAPI!
