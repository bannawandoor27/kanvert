import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, SubscriptionTier } from '../types';
import { STORAGE_KEYS } from '../constants';
import { storage } from '../utils';
import { api } from '../services/api';

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
  requestPasswordReset: (email: string) => Promise<boolean>;
  confirmPasswordReset: (email: string, token: string, newPassword: string) => Promise<boolean>;
  refreshUser: () => Promise<void>;
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
          const response = await api.auth.login({ email, password, remember_me: false });
          
          if (response.error) {
            set({ error: response.error, isLoading: false });
            return false;
          }
          
          if (response.data) {
            // Store auth token
            storage.set(STORAGE_KEYS.AUTH_TOKEN, response.data.access_token);
            storage.set(STORAGE_KEYS.API_KEY, response.data.user.api_key);
            
            // Create user object with proper typing
            const user: User = {
              id: response.data.user.id,
              email: response.data.user.email,
              name: response.data.user.name,
              subscription: response.data.user.subscription || SubscriptionTier.FREE,
              api_key: response.data.user.api_key,
              created_at: response.data.user.created_at || new Date().toISOString(),
              last_login: new Date().toISOString(),
            };
            
            set({ 
              user, 
              isAuthenticated: true, 
              isLoading: false 
            });
            
            return true;
          }
          
          return false;
        } catch (error) {
          set({ 
            error: 'Login failed. Please try again.', 
            isLoading: false 
          });
          return false;
        }
      },
      
      register: async (email: string, password: string, name: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const [firstName, ...lastNameParts] = name.split(' ');
          const lastName = lastNameParts.join(' ') || '';
          
          const response = await api.auth.register({
            first_name: firstName,
            last_name: lastName,
            email,
            password,
            terms_accepted: true,
            newsletter_subscription: false,
          });
          
          if (response.error) {
            set({ error: response.error, isLoading: false });
            return false;
          }
          
          if (response.data) {
            // Store auth token
            storage.set(STORAGE_KEYS.AUTH_TOKEN, response.data.access_token);
            storage.set(STORAGE_KEYS.API_KEY, response.data.user.api_key);
            
            // Create user object with proper typing
            const user: User = {
              id: response.data.user.id,
              email: response.data.user.email,
              name: response.data.user.name,
              subscription: response.data.user.subscription || SubscriptionTier.FREE,
              api_key: response.data.user.api_key,
              created_at: response.data.user.created_at || new Date().toISOString(),
              last_login: new Date().toISOString(),
            };
            
            set({ 
              user, 
              isAuthenticated: true, 
              isLoading: false 
            });
            
            return true;
          }
          
          return false;
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
      
      requestPasswordReset: async (email: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await api.auth.requestPasswordReset({ email });
          
          if (response.error) {
            set({ error: response.error, isLoading: false });
            return false;
          }
          
          set({ isLoading: false });
          return true;
        } catch (error) {
          set({ 
            error: 'Failed to send password reset email', 
            isLoading: false 
          });
          return false;
        }
      },
      
      confirmPasswordReset: async (email: string, token: string, newPassword: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await api.auth.confirmPasswordReset({
            email,
            token,
            new_password: newPassword,
          });
          
          if (response.error) {
            set({ error: response.error, isLoading: false });
            return false;
          }
          
          set({ isLoading: false });
          return true;
        } catch (error) {
          set({ 
            error: 'Failed to reset password', 
            isLoading: false 
          });
          return false;
        }
      },
      
      refreshUser: async () => {
        const token = storage.get(STORAGE_KEYS.AUTH_TOKEN);
        if (!token) return;
        
        try {
          const response = await api.auth.getCurrentUser();
          
          if (response.data && !response.error) {
            const user: User = {
              id: response.data._id || response.data.id,
              email: response.data.email,
              name: response.data.name,
              subscription: response.data.subscription || SubscriptionTier.FREE,
              api_key: response.data.api_key,
              created_at: response.data.created_at,
              last_login: response.data.last_login,
            };
            
            set({ user, isAuthenticated: true });
          }
        } catch (error) {
          // If token is invalid, clear auth state
          storage.remove(STORAGE_KEYS.AUTH_TOKEN);
          storage.remove(STORAGE_KEYS.API_KEY);
          storage.remove(STORAGE_KEYS.USER);
          set({ user: null, isAuthenticated: false });
        }
      },
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