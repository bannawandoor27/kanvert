import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, SubscriptionTier } from '../types';
import { STORAGE_KEYS } from '../constants';
import { storage } from '../utils';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, name: string) => Promise<boolean>;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          // Simulate API call - replace with actual authentication
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Mock user data - replace with actual API response
          const mockUser: User = {
            id: '1',
            email,
            name: email.split('@')[0],
            subscription: SubscriptionTier.FREE,
            api_key: 'sk-' + Math.random().toString(36).substr(2, 32),
            created_at: new Date().toISOString(),
            last_login: new Date().toISOString(),
          };
          
          // Store auth token
          storage.set(STORAGE_KEYS.AUTH_TOKEN, 'mock-jwt-token');
          storage.set(STORAGE_KEYS.API_KEY, mockUser.api_key);
          
          set({ 
            user: mockUser, 
            isAuthenticated: true, 
            isLoading: false 
          });
          
          return true;
        } catch (error) {
          set({ 
            error: 'Invalid email or password', 
            isLoading: false 
          });
          return false;
        }
      },
      
      register: async (email: string, password: string, name: string) => {
        set({ isLoading: true, error: null });
        
        try {
          // Simulate API call - replace with actual registration
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Mock user data - replace with actual API response
          const mockUser: User = {
            id: Math.random().toString(36).substr(2, 9),
            email,
            name,
            subscription: SubscriptionTier.FREE,
            api_key: 'sk-' + Math.random().toString(36).substr(2, 32),
            created_at: new Date().toISOString(),
          };
          
          // Store auth token
          storage.set(STORAGE_KEYS.AUTH_TOKEN, 'mock-jwt-token');
          storage.set(STORAGE_KEYS.API_KEY, mockUser.api_key);
          
          set({ 
            user: mockUser, 
            isAuthenticated: true, 
            isLoading: false 
          });
          
          return true;
        } catch (error) {
          set({ 
            error: 'Registration failed. Please try again.', 
            isLoading: false 
          });
          return false;
        }
      },
      
      logout: () => {
        storage.remove(STORAGE_KEYS.AUTH_TOKEN);
        storage.remove(STORAGE_KEYS.API_KEY);
        storage.remove(STORAGE_KEYS.USER);
        
        set({ 
          user: null, 
          isAuthenticated: false, 
          error: null 
        });
      },
      
      updateUser: (updates: Partial<User>) => {
        const { user } = get();
        if (user) {
          const updatedUser = { ...user, ...updates };
          set({ user: updatedUser });
        }
      },
      
      clearError: () => set({ error: null }),
      
      setLoading: (loading: boolean) => set({ isLoading: loading }),
    }),
    {
      name: STORAGE_KEYS.USER,
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);