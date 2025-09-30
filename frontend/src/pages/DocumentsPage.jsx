import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  FileText, 
  Trash2, 
  Check, 
  X, 
  AlertCircle,
  Loader2,
  File,
  Calendar,
  HardDrive,
  Eye
} from 'lucide-react';
import { documentsAPI, embeddingAPI } from '../services/api';
import FileUpload from '../components/FileUpload';
import LoadingSpinner from '../components/LoadingSpinner';
import { apiUtils } from '../services/api';

const DocumentsPage = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [embedding, setEmbedding] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await documentsAPI.getAll();
      setDocuments(response.data.documents || []);
    } catch (error) {
      setError('Không thể tải danh sách tài liệu: ' + apiUtils.getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    try {
      setUploading(true);
      setError('');
      
      const response = await documentsAPI.upload(file);
      setSuccess(`Tài liệu "${file.name}" đã được upload thành công!`);
      
      // Reload documents list
      await loadDocuments();
      
      // Auto-embed the document
      if (response.data.document_id) {
        await handleEmbedDocument(response.data.document_id);
      }
    } catch (error) {
      setError('Lỗi upload: ' + apiUtils.getErrorMessage(error));
    } finally {
      setUploading(false);
    }
  };

  const handleEmbedDocument = async (docId) => {
    try {
      setEmbedding(prev => ({ ...prev, [docId]: 'processing' }));
      setError('');
      
      const response = await embeddingAPI.embedDocument(docId);
      setSuccess(`Tài liệu đã được embedding thành công! (${response.data.chunks_processed} chunks)`);
      
      setEmbedding(prev => ({ ...prev, [docId]: 'completed' }));
    } catch (error) {
      setError('Lỗi embedding: ' + apiUtils.getErrorMessage(error));
      setEmbedding(prev => ({ ...prev, [docId]: 'error' }));
    }
  };

  const handleDeleteDocument = async (docId, filename) => {
    if (!window.confirm(`Bạn có chắc chắn muốn xóa tài liệu "${filename}"?`)) {
      return;
    }

    try {
      setError('');
      await documentsAPI.delete(docId);
      setSuccess(`Tài liệu "${filename}" đã được xóa thành công!`);
      
      // Remove from local state
      setDocuments(prev => prev.filter(doc => doc.id !== docId));
    } catch (error) {
      setError('Lỗi xóa tài liệu: ' + apiUtils.getErrorMessage(error));
    }
  };

  const handleSelectDocument = async (docId) => {
    try {
      setError('');
      await documentsAPI.select(docId);
      setSuccess('Tài liệu đã được chọn để chat!');
    } catch (error) {
      setError('Lỗi chọn tài liệu: ' + apiUtils.getErrorMessage(error));
    }
  };

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return '📄';
    if (ext === 'txt') return '📝';
    return '📄';
  };

  const getEmbeddingStatus = (docId) => {
    const status = embedding[docId];
    if (status === 'processing') return { text: 'Đang embedding...', color: 'text-yellow-600', icon: Loader2 };
    if (status === 'completed') return { text: 'Đã embedding', color: 'text-green-600', icon: Check };
    if (status === 'error') return { text: 'Lỗi embedding', color: 'text-red-600', icon: X };
    return { text: 'Chưa embedding', color: 'text-gray-500', icon: AlertCircle };
  };

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(clearMessages, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">Đang tải tài liệu...</span>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Quản lý Tài liệu
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Upload và quản lý tài liệu cho hệ thống RAG
          </p>
        </div>
        
        <div className="text-sm text-gray-500 dark:text-gray-400">
          Tổng: {documents.length} tài liệu
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            <p className="text-red-700 dark:text-red-400">{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <div className="flex items-center">
            <Check className="w-5 h-5 text-green-500 mr-2" />
            <p className="text-green-700 dark:text-green-400">{success}</p>
          </div>
        </div>
      )}

      {/* Upload Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Upload Tài liệu
        </h2>
        <FileUpload
          onUpload={handleFileUpload}
          onRemove={() => {}}
          acceptedFiles={[]}
        />
      </div>

      {/* Documents List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Danh sách Tài liệu
          </h2>
        </div>

        {documents.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Chưa có tài liệu nào
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Hãy upload tài liệu đầu tiên để bắt đầu sử dụng hệ thống RAG
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {documents.map((doc) => {
              const embeddingStatus = getEmbeddingStatus(doc.id);
              const StatusIcon = embeddingStatus.icon;
              
              return (
                <div key={doc.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-3xl">{getFileIcon(doc.filename)}</div>
                      
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                            {doc.filename}
                          </h3>
                          {doc.selected && (
                            <span className="px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
                              Đã chọn
                            </span>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                          <div className="flex items-center space-x-1">
                            <HardDrive className="w-4 h-4" />
                            <span>{apiUtils.formatFileSize(doc.size)}</span>
                          </div>
                          
                          <div className="flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>{apiUtils.formatDate(doc.uploaded_at)}</span>
                          </div>
                          
                          <div className="flex items-center space-x-1">
                            <StatusIcon className={`w-4 h-4 ${embeddingStatus.color} ${
                              embeddingStatus.text === 'Đang embedding...' ? 'animate-spin' : ''
                            }`} />
                            <span className={embeddingStatus.color}>
                              {embeddingStatus.text}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {/* Embed Button */}
                      {embeddingStatus.text !== 'Đang embedding...' && embeddingStatus.text !== 'Đã embedding' && (
                        <button
                          onClick={() => handleEmbedDocument(doc.id)}
                          className="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                        >
                          Embed
                        </button>
                      )}
                      
                      {/* Select Button */}
                      {!doc.selected && (
                        <button
                          onClick={() => handleSelectDocument(doc.id)}
                          className="px-3 py-1 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                        >
                          Chọn
                        </button>
                      )}
                      
                      {/* View Button */}
                      <button
                        onClick={() => window.open(`/api/documents/${doc.id}`, '_blank')}
                        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                        title="Xem tài liệu"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      
                      {/* Delete Button */}
                      <button
                        onClick={() => handleDeleteDocument(doc.id, doc.filename)}
                        className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                        title="Xóa tài liệu"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Stats */}
      {documents.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center">
              <File className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Tổng tài liệu</p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {documents.length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center">
              <Check className="w-8 h-8 text-green-600 dark:text-green-400" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Đã embedding</p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {Object.values(embedding).filter(status => status === 'completed').length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center">
              <HardDrive className="w-8 h-8 text-purple-600 dark:text-purple-400" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Tổng dung lượng</p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {apiUtils.formatFileSize(documents.reduce((sum, doc) => sum + doc.size, 0))}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentsPage;
