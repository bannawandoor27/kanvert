import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { useNotificationStore } from '../stores';
import type { 
  ConversionHistoryResponse, 
  ConversionHistoryItem,
  BulkActionRequest,
  ConversionFilters 
} from '../types';

// Query keys for history
export const historyQueryKeys = {
  all: ['history'] as const,
  lists: () => [...historyQueryKeys.all, 'list'] as const,
  list: (params?: any) => [...historyQueryKeys.lists(), params] as const,
  details: () => [...historyQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...historyQueryKeys.details(), id] as const,
  stats: () => [...historyQueryKeys.all, 'stats'] as const,
  summary: (days?: number) => [...historyQueryKeys.stats(), 'summary', days] as const,
  daily: (days?: number) => [...historyQueryKeys.stats(), 'daily', days] as const,
};

// Conversion History List Hook
export const useConversionHistory = (params: {
  page?: number;
  per_page?: number;
  search?: string;
  status?: string;
  format?: string;
  start_date?: string;
  end_date?: string;
  sort_field?: string;
  sort_order?: 'asc' | 'desc';
} = {}) => {
  return useQuery({
    queryKey: historyQueryKeys.list(params),
    queryFn: async () => {
      const response = await api.history.getHistory(params);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    keepPreviousData: true, // Keep previous page data while loading new page
  });
};

// Conversion Details Hook
export const useConversionDetails = (conversionId: string) => {
  return useQuery({
    queryKey: historyQueryKeys.detail(conversionId),
    queryFn: async () => {
      const response = await api.history.getConversionDetails(conversionId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    enabled: !!conversionId, // Only run if conversionId is provided
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
};

// Delete Conversion Hook
export const useDeleteConversion = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (conversionId: string) => {
      const response = await api.history.deleteConversion(conversionId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: (_, conversionId) => {
      // Invalidate and refetch history lists
      queryClient.invalidateQueries({ queryKey: historyQueryKeys.lists() });
      // Remove the specific item from cache
      queryClient.removeQueries({ queryKey: historyQueryKeys.detail(conversionId) });
      success('Conversion Deleted', 'The conversion has been removed from your history');
    },
    onError: (err: Error) => {
      error('Deletion Failed', err.message);
    },
  });
};

// Bulk Actions Hook
export const useBulkAction = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (data: BulkActionRequest) => {
      const response = await api.history.bulkAction(data);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: (data, variables) => {
      // Invalidate history lists to reflect changes
      queryClient.invalidateQueries({ queryKey: historyQueryKeys.lists() });
      
      // Show success message based on action
      const actionMap = {
        delete: 'Conversions deleted',
        archive: 'Conversions archived',
        download: 'Download links prepared',
      };
      
      const message = actionMap[variables.action as keyof typeof actionMap] || 'Bulk action completed';
      success('Bulk Action Completed', `${message} successfully`);
    },
    onError: (err: Error) => {
      error('Bulk Action Failed', err.message);
    },
  });
};

// History Statistics Hook
export const useHistoryStats = (days = 30) => {
  return useQuery({
    queryKey: historyQueryKeys.summary(days),
    queryFn: async () => {
      const response = await api.history.getHistoryStats(days);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
};

// Daily Statistics Hook
export const useDailyStats = (days = 30) => {
  return useQuery({
    queryKey: historyQueryKeys.daily(days),
    queryFn: async () => {
      const response = await api.history.getDailyStats(days);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
};

// Export History Hook
export const useExportHistory = () => {
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (params: {
      filters?: ConversionFilters;
      format?: 'csv' | 'json';
    }) => {
      const response = await api.history.exportHistory(params.filters, params.format);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (data: any) => {
      // Handle the exported data
      if (data.format === 'csv') {
        // Create and download CSV file
        const blob = new Blob([data.content], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = data.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else {
        // Handle JSON export
        const blob = new Blob([JSON.stringify(data.content, null, 2)], { 
          type: 'application/json' 
        });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = data.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
      
      success('Export Complete', `Your conversion history has been exported as ${data.format.toUpperCase()}`);
    },
    onError: (err: Error) => {
      error('Export Failed', err.message);
    },
  });
};

// Combined history data hook
export const useHistoryData = (
  listParams: Parameters<typeof useConversionHistory>[0] = {},
  statsEnabled = true,
  statsDays = 30
) => {
  const historyQuery = useConversionHistory(listParams);
  const statsQuery = useHistoryStats(statsDays);
  const dailyStatsQuery = useDailyStats(statsDays);

  return {
    history: historyQuery,
    stats: statsEnabled ? statsQuery : { data: null, isLoading: false, error: null },
    dailyStats: statsEnabled ? dailyStatsQuery : { data: null, isLoading: false, error: null },
    isLoading: historyQuery.isLoading || (statsEnabled && (statsQuery.isLoading || dailyStatsQuery.isLoading)),
    hasError: historyQuery.error || (statsEnabled && (statsQuery.error || dailyStatsQuery.error)),
    isSuccess: historyQuery.isSuccess && (!statsEnabled || (statsQuery.isSuccess && dailyStatsQuery.isSuccess)),
  };
};

// Refresh history data
export const useRefreshHistory = () => {
  const queryClient = useQueryClient();
  const { success } = useNotificationStore();

  return useMutation({
    mutationFn: async () => {
      await queryClient.invalidateQueries({
        queryKey: historyQueryKeys.all,
      });
    },
    onSuccess: () => {
      success('History Refreshed', 'Conversion history has been updated');
    },
  });
};

// Prefetch history hook
export const usePrefetchHistory = () => {
  const queryClient = useQueryClient();

  const prefetchConversionHistory = (params: Parameters<typeof useConversionHistory>[0] = {}) => {
    return queryClient.prefetchQuery({
      queryKey: historyQueryKeys.list(params),
      queryFn: async () => {
        const response = await api.history.getHistory(params);
        if (response.error) {
          throw new Error(response.error);
        }
        return response.data!;
      },
      staleTime: 2 * 60 * 1000,
    });
  };

  const prefetchHistoryStats = (days = 30) => {
    return queryClient.prefetchQuery({
      queryKey: historyQueryKeys.summary(days),
      queryFn: async () => {
        const response = await api.history.getHistoryStats(days);
        if (response.error) {
          throw new Error(response.error);
        }
        return response.data!;
      },
      staleTime: 5 * 60 * 1000,
    });
  };

  return {
    prefetchConversionHistory,
    prefetchHistoryStats,
  };
};