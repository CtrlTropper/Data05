import React, { useEffect, useState } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';

const Toast = ({ 
  message, 
  type = 'info', 
  duration = 5000, 
  onClose 
}) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(onClose, 300); // Wait for animation to complete
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300);
  };

  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertTriangle,
    info: Info,
  };

  const colors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500',
  };

  const Icon = icons[type];

  return (
    <div
      className={`fixed top-4 right-4 z-50 max-w-sm w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 transform transition-all duration-300 ${
        isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      }`}
    >
      <div className="p-4">
        <div className="flex items-start">
          <div className={`flex-shrink-0 w-6 h-6 rounded-full ${colors[type]} flex items-center justify-center`}>
            <Icon className="w-4 h-4 text-white" />
          </div>
          <div className="ml-3 flex-1">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {message}
            </p>
          </div>
          <button
            onClick={handleClose}
            className="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Toast;
