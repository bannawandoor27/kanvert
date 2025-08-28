import React from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import { cn } from '../../utils';

interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  onDismiss: () => void;
}

const Toast: React.FC<ToastProps> = ({ id, type, title, message, onDismiss }) => {
  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertTriangle,
    info: Info,
  };
  
  const colors = {
    success: 'text-green-600 bg-green-50 border-green-200',
    error: 'text-red-600 bg-red-50 border-red-200',
    warning: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    info: 'text-blue-600 bg-blue-50 border-blue-200',
  };
  
  const Icon = icons[type];
  
  return (
    <div
      className={cn(
        'flex items-start space-x-3 p-4 rounded-lg border shadow-lg max-w-md w-full',
        colors[type]
      )}
    >
      <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900">
          {title}
        </p>
        <p className="text-sm text-gray-600 mt-1">
          {message}
        </p>
      </div>
      
      <button
        onClick={onDismiss}
        className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};

// Custom toast functions
export const showToast = {
  success: (title: string, message: string) => {
    toast.custom((t) => (
      <Toast
        id={t.id}
        type="success"
        title={title}
        message={message}
        onDismiss={() => toast.dismiss(t.id)}
      />
    ), {
      duration: 4000,
    });
  },
  
  error: (title: string, message: string) => {
    toast.custom((t) => (
      <Toast
        id={t.id}
        type="error"
        title={title}
        message={message}
        onDismiss={() => toast.dismiss(t.id)}
      />
    ), {
      duration: 6000,
    });
  },
  
  warning: (title: string, message: string) => {
    toast.custom((t) => (
      <Toast
        id={t.id}
        type="warning"
        title={title}
        message={message}
        onDismiss={() => toast.dismiss(t.id)}
      />
    ), {
      duration: 5000,
    });
  },
  
  info: (title: string, message: string) => {
    toast.custom((t) => (
      <Toast
        id={t.id}
        type="info"
        title={title}
        message={message}
        onDismiss={() => toast.dismiss(t.id)}
      />
    ), {
      duration: 4000,
    });
  },
};

// Toast container component
export const ToastContainer: React.FC = () => {
  return (
    <Toaster
      position="top-right"
      containerStyle={{
        top: 20,
        right: 20,
      }}
      toastOptions={{
        duration: 4000,
        style: {
          background: 'transparent',
          boxShadow: 'none',
          padding: 0,
        },
      }}
    />
  );
};

export default Toast;