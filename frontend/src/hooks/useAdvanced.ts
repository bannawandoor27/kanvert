import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { useNotificationStore } from '../stores';
import type { 
  BatchJob, 
  ConversionTemplate, 
  ScheduledJob 
} from '../types';

// Query keys for advanced features
export const advancedQueryKeys = {
  all: ['advanced'] as const,
  
  // Batch Jobs
  batchJobs: () => [...advancedQueryKeys.all, 'batch-jobs'] as const,
  batchJobsList: (limit?: number, offset?: number) => [...advancedQueryKeys.batchJobs(), 'list', { limit, offset }] as const,
  batchJob: (id: string) => [...advancedQueryKeys.batchJobs(), 'detail', id] as const,
  
  // Templates
  templates: () => [...advancedQueryKeys.all, 'templates'] as const,
  templatesList: () => [...advancedQueryKeys.templates(), 'list'] as const,
  template: (id: string) => [...advancedQueryKeys.templates(), 'detail', id] as const,
  
  // Scheduled Jobs
  scheduledJobs: () => [...advancedQueryKeys.all, 'scheduled-jobs'] as const,
  scheduledJobsList: () => [...advancedQueryKeys.scheduledJobs(), 'list'] as const,
  scheduledJob: (id: string) => [...advancedQueryKeys.scheduledJobs(), 'detail', id] as const,
};

// =============================================================================
// BATCH JOBS HOOKS
// =============================================================================

// Get Batch Jobs List
export const useBatchJobs = (limit = 20, offset = 0) => {
  return useQuery({
    queryKey: advancedQueryKeys.batchJobsList(limit, offset),
    queryFn: async () => {
      const response = await api.advanced.getBatchJobs(limit, offset);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    keepPreviousData: true,
  });
};

// Get Single Batch Job
export const useBatchJob = (jobId: string) => {
  return useQuery({
    queryKey: advancedQueryKeys.batchJob(jobId),
    queryFn: async () => {
      const response = await api.advanced.getBatchJob(jobId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    enabled: !!jobId,
    staleTime: 30 * 1000, // 30 seconds for active jobs
    gcTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: (data) => {
      // Auto-refresh if job is processing
      return data?.status === 'processing' ? 5000 : false; // 5 seconds
    },
  });
};

// Create Batch Job
export const useCreateBatchJob = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (data: { name: string; options: any }) => {
      const response = await api.advanced.createBatchJob(data);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.batchJobs() });
      success('Batch Job Created', `Batch job "${data.name}" has been created successfully`);
    },
    onError: (err: Error) => {
      error('Creation Failed', err.message);
    },
  });
};

// Add Files to Batch Job
export const useAddFilesToBatchJob = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async ({ jobId, files }: { jobId: string; files: File[] }) => {
      const response = await api.advanced.addFilesToBatchJob(jobId, files);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.batchJob(variables.jobId) });
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.batchJobs() });
      success('Files Added', `${variables.files.length} files added to batch job`);
    },
    onError: (err: Error) => {
      error('Upload Failed', err.message);
    },
  });
};

// Start Batch Job
export const useStartBatchJob = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (jobId: string) => {
      const response = await api.advanced.startBatchJob(jobId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: (_, jobId) => {
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.batchJob(jobId) });
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.batchJobs() });
      success('Batch Job Started', 'The batch processing has begun');
    },
    onError: (err: Error) => {
      error('Start Failed', err.message);
    },
  });
};

// Pause Batch Job
export const usePauseBatchJob = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (jobId: string) => {
      const response = await api.advanced.pauseBatchJob(jobId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: (_, jobId) => {
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.batchJob(jobId) });
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.batchJobs() });
      success('Batch Job Paused', 'The batch processing has been paused');
    },
    onError: (err: Error) => {
      error('Pause Failed', err.message);
    },
  });
};

// Cancel Batch Job
export const useCancelBatchJob = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (jobId: string) => {
      const response = await api.advanced.cancelBatchJob(jobId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: (_, jobId) => {
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.batchJob(jobId) });
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.batchJobs() });
      success('Batch Job Cancelled', 'The batch processing has been cancelled');
    },
    onError: (err: Error) => {
      error('Cancel Failed', err.message);
    },
  });
};

// =============================================================================
// TEMPLATES HOOKS
// =============================================================================

// Get Templates List
export const useTemplates = () => {
  return useQuery({
    queryKey: advancedQueryKeys.templatesList(),
    queryFn: async () => {
      const response = await api.advanced.getTemplates();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  });
};

// Create Template
export const useCreateTemplate = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (data: {
      name: string;
      description: string;
      input_format: string;
      output_format: string;
      options: any;
    }) => {
      const response = await api.advanced.createTemplate(data);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.templates() });
      success('Template Created', `Template "${data.name}" has been created successfully`);
    },
    onError: (err: Error) => {
      error('Creation Failed', err.message);
    },
  });
};

// Update Template
export const useUpdateTemplate = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async ({ templateId, data }: { 
      templateId: string; 
      data: Partial<ConversionTemplate> 
    }) => {
      const response = await api.advanced.updateTemplate(templateId, data);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.templates() });
      success('Template Updated', `Template "${data.name}" has been updated successfully`);
    },
    onError: (err: Error) => {
      error('Update Failed', err.message);
    },
  });
};

// Delete Template
export const useDeleteTemplate = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (templateId: string) => {
      const response = await api.advanced.deleteTemplate(templateId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.templates() });
      success('Template Deleted', 'The template has been removed successfully');
    },
    onError: (err: Error) => {
      error('Deletion Failed', err.message);
    },
  });
};

// =============================================================================
// SCHEDULED JOBS HOOKS
// =============================================================================

// Get Scheduled Jobs List
export const useScheduledJobs = () => {
  return useQuery({
    queryKey: advancedQueryKeys.scheduledJobsList(),
    queryFn: async () => {
      const response = await api.advanced.getScheduledJobs();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Create Scheduled Job
export const useCreateScheduledJob = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (data: {
      name: string;
      template_id: string;
      schedule_type: string;
      schedule_time: string;
      options: any;
    }) => {
      const response = await api.advanced.createScheduledJob(data);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.scheduledJobs() });
      success('Scheduled Job Created', `Scheduled job "${data.name}" has been created`);
    },
    onError: (err: Error) => {
      error('Creation Failed', err.message);
    },
  });
};

// Update Scheduled Job
export const useUpdateScheduledJob = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async ({ jobId, data }: { 
      jobId: string; 
      data: Partial<ScheduledJob> 
    }) => {
      const response = await api.advanced.updateScheduledJob(jobId, data);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.scheduledJobs() });
      success('Scheduled Job Updated', `Job "${data.name}" has been updated successfully`);
    },
    onError: (err: Error) => {
      error('Update Failed', err.message);
    },
  });
};

// Delete Scheduled Job
export const useDeleteScheduledJob = () => {
  const queryClient = useQueryClient();
  const { success, error } = useNotificationStore();

  return useMutation({
    mutationFn: async (jobId: string) => {
      const response = await api.advanced.deleteScheduledJob(jobId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: advancedQueryKeys.scheduledJobs() });
      success('Scheduled Job Deleted', 'The scheduled job has been removed');
    },
    onError: (err: Error) => {
      error('Deletion Failed', err.message);
    },
  });
};

// =============================================================================
// COMBINED HOOKS
// =============================================================================

// Combined advanced features data
export const useAdvancedData = () => {
  const batchJobsQuery = useBatchJobs();
  const templatesQuery = useTemplates();
  const scheduledJobsQuery = useScheduledJobs();

  return {
    batchJobs: batchJobsQuery,
    templates: templatesQuery,
    scheduledJobs: scheduledJobsQuery,
    isLoading: batchJobsQuery.isLoading || templatesQuery.isLoading || scheduledJobsQuery.isLoading,
    hasError: batchJobsQuery.error || templatesQuery.error || scheduledJobsQuery.error,
    isSuccess: batchJobsQuery.isSuccess && templatesQuery.isSuccess && scheduledJobsQuery.isSuccess,
  };
};

// Refresh all advanced features data
export const useRefreshAdvanced = () => {
  const queryClient = useQueryClient();
  const { success } = useNotificationStore();

  return useMutation({
    mutationFn: async () => {
      await queryClient.invalidateQueries({
        queryKey: advancedQueryKeys.all,
      });
    },
    onSuccess: () => {
      success('Advanced Features Refreshed', 'All advanced features data has been updated');
    },
  });
};