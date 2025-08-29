import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { useNotificationStore } from '../stores';
import type { DashboardSummary, AnalyticsData } from '../types';

// Query keys for dashboard
export const dashboardQueryKeys = {
  all: ['dashboard'] as const,
  summary: (period?: string) => [...dashboardQueryKeys.all, 'summary', period] as const,
  analytics: (timeRange?: string) => [...dashboardQueryKeys.all, 'analytics', timeRange] as const,
  systemStatus: () => [...dashboardQueryKeys.all, 'system-status'] as const,
};

// Dashboard Summary Hook
export const useDashboardSummary = (period: 'today' | 'week' | 'month' = 'month') => {
  return useQuery({
    queryKey: dashboardQueryKeys.summary(period),
    queryFn: async () => {
      const response = await api.dashboard.getSummary(period);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: (failureCount, error) => {
      // Don't retry on authentication errors
      if (error.message.includes('401') || error.message.includes('Unauthorized')) {
        return false;
      }
      return failureCount < 3;
    },
  });
};

// Analytics Data Hook
export const useAnalyticsData = (timeRange: 'today' | 'week' | 'month' | 'quarter' | 'year' = 'month') => {
  return useQuery({
    queryKey: dashboardQueryKeys.analytics(timeRange),
    queryFn: async () => {
      const response = await api.dashboard.getAnalytics(timeRange);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
    retry: (failureCount, error) => {
      if (error.message.includes('401') || error.message.includes('Unauthorized')) {
        return false;
      }
      return failureCount < 3;
    },
  });
};

// System Status Hook
export const useSystemStatus = () => {
  return useQuery({
    queryKey: dashboardQueryKeys.systemStatus(),
    queryFn: async () => {
      const response = await api.dashboard.getSystemStatus();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 15000, // Consider stale after 15 seconds
    gcTime: 60000, // Keep in cache for 1 minute
    retry: (failureCount, error) => {
      if (error.message.includes('401') || error.message.includes('Unauthorized')) {
        return false;
      }
      return failureCount < 2; // Less retries for system status
    },
  });
};

// Hook to refresh dashboard data
export const useRefreshDashboard = () => {
  const queryClient = useQueryClient();
  const { success } = useNotificationStore();

  return useMutation({
    mutationFn: async () => {
      // Invalidate all dashboard queries to trigger refetch
      await queryClient.invalidateQueries({
        queryKey: dashboardQueryKeys.all,
      });
    },
    onSuccess: () => {
      success('Dashboard Refreshed', 'Dashboard data has been updated');
    },
  });
};

// Combined dashboard data hook (for convenience)
export const useDashboardData = (period: 'today' | 'week' | 'month' = 'month') => {
  const summaryQuery = useDashboardSummary(period);
  const analyticsQuery = useAnalyticsData(period);
  const systemStatusQuery = useSystemStatus();

  return {
    summary: summaryQuery,
    analytics: analyticsQuery,
    systemStatus: systemStatusQuery,
    isLoading: summaryQuery.isLoading || analyticsQuery.isLoading || systemStatusQuery.isLoading,
    hasError: summaryQuery.error || analyticsQuery.error || systemStatusQuery.error,
    isSuccess: summaryQuery.isSuccess && analyticsQuery.isSuccess && systemStatusQuery.isSuccess,
  };
};

// Prefetch dashboard data hook
export const usePrefetchDashboard = () => {
  const queryClient = useQueryClient();

  const prefetchSummary = (period: 'today' | 'week' | 'month' = 'month') => {
    return queryClient.prefetchQuery({
      queryKey: dashboardQueryKeys.summary(period),
      queryFn: async () => {
        const response = await api.dashboard.getSummary(period);
        if (response.error) {
          throw new Error(response.error);
        }
        return response.data!;
      },
      staleTime: 5 * 60 * 1000,
    });
  };

  const prefetchAnalytics = (timeRange: 'today' | 'week' | 'month' | 'quarter' | 'year' = 'month') => {
    return queryClient.prefetchQuery({
      queryKey: dashboardQueryKeys.analytics(timeRange),
      queryFn: async () => {
        const response = await api.dashboard.getAnalytics(timeRange);
        if (response.error) {
          throw new Error(response.error);
        }
        return response.data!;
      },
      staleTime: 5 * 60 * 1000,
    });
  };

  return {
    prefetchSummary,
    prefetchAnalytics,
  };
};