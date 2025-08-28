import { create } from 'zustand';
import type { NotificationMessage } from '../types';
import { generateId } from '../utils';

interface NotificationState {
  notifications: NotificationMessage[];
  
  // Actions
  addNotification: (notification: Omit<NotificationMessage, 'id' | 'timestamp' | 'read'>) => void;
  removeNotification: (id: string) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearAll: () => void;
  
  // Convenience methods
  success: (title: string, message: string, action?: { label: string; url: string }) => void;
  error: (title: string, message: string, action?: { label: string; url: string }) => void;
  warning: (title: string, message: string, action?: { label: string; url: string }) => void;
  info: (title: string, message: string, action?: { label: string; url: string }) => void;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  
  addNotification: (notification) => {
    const newNotification: NotificationMessage = {
      ...notification,
      id: generateId(),
      timestamp: new Date().toISOString(),
      read: false,
    };
    
    set(state => ({
      notifications: [newNotification, ...state.notifications].slice(0, 50) // Keep max 50 notifications
    }));
    
    // Auto-remove notification after 5 seconds for success/info messages
    if (notification.type === 'success' || notification.type === 'info') {
      setTimeout(() => {
        get().removeNotification(newNotification.id);
      }, 5000);
    }
  },
  
  removeNotification: (id: string) => {
    set(state => ({
      notifications: state.notifications.filter(notification => notification.id !== id)
    }));
  },
  
  markAsRead: (id: string) => {
    set(state => ({
      notifications: state.notifications.map(notification => 
        notification.id === id 
          ? { ...notification, read: true }
          : notification
      )
    }));
  },
  
  markAllAsRead: () => {
    set(state => ({
      notifications: state.notifications.map(notification => ({
        ...notification,
        read: true
      }))
    }));
  },
  
  clearAll: () => {
    set({ notifications: [] });
  },
  
  // Convenience methods
  success: (title: string, message: string, action?) => {
    get().addNotification({
      type: 'success',
      title,
      message,
      action
    });
  },
  
  error: (title: string, message: string, action?) => {
    get().addNotification({
      type: 'error',
      title,
      message,
      action
    });
  },
  
  warning: (title: string, message: string, action?) => {
    get().addNotification({
      type: 'warning',
      title,
      message,
      action
    });
  },
  
  info: (title: string, message: string, action?) => {
    get().addNotification({
      type: 'info',
      title,
      message,
      action
    });
  },
}));