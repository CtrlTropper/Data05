import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, AlertCircle } from 'lucide-react';

const FileUpload = ({ onUpload, onRemove, acceptedFiles = [], maxSize = 50 * 1024 * 1024 }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
    setError('');
    
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0]?.code === 'file-too-large') {
        setError('File quá lớn. Kích thước tối đa là 50MB.');
      } else if (rejection.errors[0]?.code === 'file-invalid-type') {
        setError('Định dạng file không được hỗ trợ. Chỉ chấp nhận PDF và TXT.');
      } else {
        setError('Có lỗi xảy ra khi upload file.');
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      setUploading(true);
      try {
        await onUpload(acceptedFiles[0]);
      } catch (err) {
        setError(err.message || 'Có lỗi xảy ra khi upload file.');
      } finally {
        setUploading(false);
      }
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
    maxSize,
    multiple: false,
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    return ext === 'pdf' ? '📄' : '📝';
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} disabled={uploading} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        {uploading ? (
          <div className="space-y-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Đang upload...</p>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-lg font-medium text-gray-900 dark:text-white">
              {isDragActive ? 'Thả file vào đây' : 'Kéo thả file hoặc click để chọn'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Hỗ trợ PDF, TXT (tối đa 50MB)
            </p>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
          <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Uploaded Files */}
      {acceptedFiles.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
            Files đã upload:
          </h3>
          {acceptedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{getFileIcon(file.filename)}</span>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {file.filename}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {formatFileSize(file.size)} • {file.uploaded_at}
                  </p>
                </div>
              </div>
              <button
                onClick={() => onRemove(file.id)}
                className="text-gray-400 hover:text-red-500 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
