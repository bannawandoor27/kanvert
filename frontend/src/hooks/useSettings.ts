import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { useNotificationStore } from '../stores';
import type { 
  UserProfile, 
  NotificationSettings, 
  ConversionDefaults, 
  APIKeyInfo,
  PasswordChangeRequest 
} from '../types';

// Query keys for settings
export const settingsQueryKeys = {
  all: ['settings'] as const,
  profile: () => [...settingsQueryKeys.all, 'profile'] as const,
  notifications: () => [...settingsQueryKeys.all, 'notifications'] as const,
  conversionDefaults: () => [...settingsQueryKeys.all, 'conversion-defaults'] as const,
  apiKeys: () => [...settingsQueryKeys.all, 'api-keys'] as const,
  usageStats: () => [...settingsQueryKeys.all, 'usage-stats'] as const,
  allSettings: () => [...settingsQueryKeys.all, 'all'] as const,
};

// Profile Hooks
export const useUserProfile = () => {
  return useQuery({
    queryKey: settingsQueryKeys.profile(),
    queryFn: async () => {
      const response = await api.settings.getProfile();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useUpdateProfile = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (data: UserProfile) => {
      const response = await api.settings.updateProfile(data);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.profile() });
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.allSettings() });
      success('Profile Updated', 'Your profile has been successfully updated');
    },
    onError: (err: Error) => {
      error('Update Failed', err.message);
    },
  });
};

// Notification Settings Hooks
export const useNotificationSettings = () => {
  return useQuery({
    queryKey: settingsQueryKeys.notifications(),
    queryFn: async () => {
      const response = await api.settings.getNotificationSettings();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

export const useUpdateNotificationSettings = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (data: NotificationSettings) => {
      const response = await api.settings.updateNotificationSettings(data);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.notifications() });
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.allSettings() });
      success('Settings Updated', 'Your notification preferences have been saved');
    },
    onError: (err: Error) => {
      error('Update Failed', err.message);
    },
  });
};

// Conversion Defaults Hooks
export const useConversionDefaults = () => {
  return useQuery({
    queryKey: settingsQueryKeys.conversionDefaults(),
    queryFn: async () => {
      const response = await api.settings.getConversionDefaults();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
};

export const useUpdateConversionDefaults = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (data: ConversionDefaults) => {
      const response = await api.settings.updateConversionDefaults(data);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.conversionDefaults() });
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.allSettings() });
      success('Defaults Updated', 'Your conversion defaults have been saved');
    },
    onError: (err: Error) => {
      error('Update Failed', err.message);
    },
  });
};

// Password Change Hook
export const useChangePassword = () => {
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (data: PasswordChangeRequest) => {
      const response = await api.settings.changePassword(data);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: () => {
      success('Password Changed', 'Your password has been successfully updated');
    },
    onError: (err: Error) => {
      error('Password Change Failed', err.message);
    },
  });
};

// API Keys Hooks
export const useApiKeys = () => {
  return useQuery({
    queryKey: settingsQueryKeys.apiKeys(),
    queryFn: async () => {
      const response = await api.settings.getApiKeys();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 10 * 60 * 1000,
  });
};

export const useCreateApiKey = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (data: { name: string; permissions: string[] }) => {
      const response = await api.settings.createApiKey(data);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.apiKeys() });
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.allSettings() });
      success('API Key Created', `New API key \"${data.name}\" has been created successfully`);
    },
    onError: (err: Error) => {
      error('Creation Failed', err.message);
    },
  });
};

export const useRevokeApiKey = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (keyId: string) => {
      const response = await api.settings.revokeApiKey(keyId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.apiKeys() });
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.allSettings() });
      success('API Key Revoked', 'The API key has been revoked successfully');
    },
    onError: (err: Error) => {
      error('Revocation Failed', err.message);
    },
  });
};

// Usage Statistics Hook
export const useUsageStats = () => {
  return useQuery({
    queryKey: settingsQueryKeys.usageStats(),
    queryFn: async () => {
      const response = await api.settings.getUsageStats();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
};

// All Settings Hook (combined data)
export const useAllSettings = () => {
  return useQuery({
    queryKey: settingsQueryKeys.allSettings(),
    queryFn: async () => {
      const response = await api.settings.getAllSettings();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 2 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

// Combined settings hook for convenience
export const useSettingsData = () => {
  const profileQuery = useUserProfile();
  const notificationsQuery = useNotificationSettings();
  const defaultsQuery = useConversionDefaults();
  const apiKeysQuery = useApiKeys();
  const usageStatsQuery = useUsageStats();

  return {
    profile: profileQuery,
    notifications: notificationsQuery,
    defaults: defaultsQuery,
    apiKeys: apiKeysQuery,
    usageStats: usageStatsQuery,
    isLoading: [
      profileQuery.isLoading,
      notificationsQuery.isLoading,
      defaultsQuery.isLoading,
      apiKeysQuery.isLoading,
      usageStatsQuery.isLoading,
    ].some(Boolean),
    hasError: [
      profileQuery.error,
      notificationsQuery.error,
      defaultsQuery.error,
      apiKeysQuery.error,
      usageStatsQuery.error,
    ].some(Boolean),
    isSuccess: [
      profileQuery.isSuccess,
      notificationsQuery.isSuccess,
      defaultsQuery.isSuccess,
      apiKeysQuery.isSuccess,
      usageStatsQuery.isSuccess,
    ].every(Boolean),
  };
};

// Refresh all settings
export const useRefreshSettings = () => {
  const queryClient = useQueryClient();
  const { success } = useNotificationStore();

  return useMutation({
    mutationFn: async () => {
      await queryClient.invalidateQueries({
        queryKey: settingsQueryKeys.all,
      });
    },
    onSuccess: () => {
      success('Settings Refreshed', 'All settings have been updated');
    },
  });
};