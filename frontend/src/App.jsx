import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ChatPage from './pages/ChatPage';
import DocumentsPage from './pages/DocumentsPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/settings" element={
            <div className="p-6">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                Cài đặt
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Trang cài đặt sẽ được phát triển trong tương lai.
              </p>
            </div>
          } />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
