import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  ConversionRequest, 
  ConversionResponse, 
  ComparisonRequest, 
  ComparisonResponse,
  OfficeConversionRequest 
} from '../types';
import { apiRequest, apiClient } from '../utils';
import { API_ENDPOINTS } from '../constants';
import { useNotificationStore, useConversionStore } from '../stores';

// Query keys
export const queryKeys = {
  health: ['health'],
  conversionHealth: ['conversion-health'],
  supportedFormats: ['supported-formats'],
  converters: ['converters'],
  conversionHistory: ['conversion-history'],
  userStats: ['user-stats'],
} as const;

// Health check queries
export const useHealthQuery = () => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => apiRequest('GET', API_ENDPOINTS.HEALTH),
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider stale after 10 seconds
  });
};

export const useConversionHealthQuery = () => {
  return useQuery({
    queryKey: queryKeys.conversionHealth,
    queryFn: () => apiRequest('GET', API_ENDPOINTS.CONVERSION_HEALTH),
    refetchInterval: 30000,
    staleTime: 10000,
  });
};

// System info queries
export const useSupportedFormatsQuery = () => {
  return useQuery({
    queryKey: queryKeys.supportedFormats,
    queryFn: () => apiRequest('GET', API_ENDPOINTS.SUPPORTED_FORMATS),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useConvertersQuery = () => {
  return useQuery({
    queryKey: queryKeys.converters,
    queryFn: () => apiRequest('GET', API_ENDPOINTS.CONVERTERS),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Conversion mutations
export const useMarkdownToPdfMutation = () => {
  const { success, error } = useNotificationStore();
  const { completeConversion, failConversion } = useConversionStore();
  
  return useMutation({
    mutationFn: async (request: ConversionRequest) => {
      const response = await apiClient.post(API_ENDPOINTS.CONVERT_MARKDOWN_TO_PDF, request, {
        responseType: 'blob'
      });
      return {
        data: response.data,
        filename: response.headers['content-disposition']?.split('filename=')[1] || 'document.pdf',
        jobId: response.headers['x-job-id']
      };
    },
    onSuccess: (data) => {
      success('Conversion Complete', 'Your Markdown document has been successfully converted to PDF');
      completeConversion({
        job_id: data.jobId,
        status: 'COMPLETED' as any,
        output_data: new Uint8Array(),
        output_filename: data.filename
      });
    },
    onError: (err: any) => {
      const errorMessage = err.response?.data?.message || 'Conversion failed';
      error('Conversion Failed', errorMessage);
      failConversion(errorMessage);
    }
  });
};

export const useHtmlToPdfMutation = () => {
  const { success, error } = useNotificationStore();
  const { completeConversion, failConversion } = useConversionStore();
  
  return useMutation({
    mutationFn: async (request: ConversionRequest) => {
      const response = await apiClient.post(API_ENDPOINTS.CONVERT_HTML_TO_PDF, request, {
        responseType: 'blob'
      });
      return {
        data: response.data,
        filename: response.headers['content-disposition']?.split('filename=')[1] || 'document.pdf',
        jobId: response.headers['x-job-id']
      };
    },
    onSuccess: (data) => {
      success('Conversion Complete', 'Your HTML document has been successfully converted to PDF');
      completeConversion({
        job_id: data.jobId,
        status: 'COMPLETED' as any,
        output_data: new Uint8Array(),
        output_filename: data.filename
      });
    },
    onError: (err: any) => {
      const errorMessage = err.response?.data?.message || 'Conversion failed';
      error('Conversion Failed', errorMessage);
      failConversion(errorMessage);
    }
  });
};

export const useDocxToPdfMutation = () => {
  const { success, error } = useNotificationStore();
  const { completeConversion, failConversion } = useConversionStore();
  
  return useMutation({
    mutationFn: async (request: ConversionRequest) => {
      const response = await apiClient.post(API_ENDPOINTS.CONVERT_DOCX_TO_PDF, request, {
        responseType: 'blob'
      });
      return {
        data: response.data,
        filename: response.headers['content-disposition']?.split('filename=')[1] || 'document.pdf',
        jobId: response.headers['x-job-id']
      };
    },
    onSuccess: (data) => {
      success('Conversion Complete', 'Your DOCX document has been successfully converted to PDF');
      completeConversion({
        job_id: data.jobId,
        status: 'COMPLETED' as any,
        output_data: new Uint8Array(),
        output_filename: data.filename
      });
    },
    onError: (err: any) => {
      const errorMessage = err.response?.data?.message || 'Conversion failed';
      error('Conversion Failed', errorMessage);
      failConversion(errorMessage);
    }
  });
};

export const useOfficeToPdfMutation = () => {
  const { success, error } = useNotificationStore();
  const { completeConversion, failConversion } = useConversionStore();
  
  return useMutation({
    mutationFn: async (request: OfficeConversionRequest) => {
      const response = await apiClient.post(API_ENDPOINTS.CONVERT_OFFICE_TO_PDF, request, {
        responseType: 'blob'
      });
      return {
        data: response.data,
        filename: response.headers['content-disposition']?.split('filename=')[1] || 'document.pdf',
        jobId: response.headers['x-job-id']
      };
    },
    onSuccess: (data) => {
      success('Conversion Complete', 'Your Office document has been successfully converted to PDF');
      completeConversion({
        job_id: data.jobId,
        status: 'COMPLETED' as any,
        output_data: new Uint8Array(),
        output_filename: data.filename
      });
    },
    onError: (err: any) => {
      const errorMessage = err.response?.data?.message || 'Conversion failed';
      error('Conversion Failed', errorMessage);
      failConversion(errorMessage);
    }
  });
};

export const useDocxCompareMutation = () => {
  const { success, error } = useNotificationStore();
  
  return useMutation({
    mutationFn: async (request: ComparisonRequest) => {
      const response = await apiRequest<ComparisonResponse>('POST', API_ENDPOINTS.COMPARE_DOCX, request);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (data) => {
      if (data.differences_found) {
        success('Comparison Complete', `Documents compared with ${(data.similarity_score * 100).toFixed(1)}% similarity`);
      } else {
        success('Comparison Complete', 'No differences found between the documents');
      }
    },
    onError: (err: any) => {
      const errorMessage = err.message || 'Document comparison failed';
      error('Comparison Failed', errorMessage);
    }
  });
};

// Generic conversion mutation
export const useGenericConversionMutation = () => {
  const { success, error } = useNotificationStore();
  const { completeConversion, failConversion } = useConversionStore();
  
  return useMutation({
    mutationFn: async ({ request, converterName }: { request: ConversionRequest; converterName?: string }) => {
      const url = converterName 
        ? `${API_ENDPOINTS.CONVERT_GENERIC}?converter_name=${converterName}`
        : API_ENDPOINTS.CONVERT_GENERIC;
        
      const response = await apiClient.post(url, request, {
        responseType: 'blob'
      });
      
      return {
        data: response.data,
        filename: response.headers['content-disposition']?.split('filename=')[1] || 'document',
        jobId: response.headers['x-job-id']
      };
    },
    onSuccess: (data) => {
      success('Conversion Complete', 'Your document has been successfully converted');
      completeConversion({
        job_id: data.jobId,
        status: 'COMPLETED' as any,
        output_data: new Uint8Array(),
        output_filename: data.filename
      });
    },
    onError: (err: any) => {
      const errorMessage = err.response?.data?.message || 'Conversion failed';
      error('Conversion Failed', errorMessage);
      failConversion(errorMessage);
    }
  });
};

// Custom hook for downloading files
export const useDownloadFile = () => {
  const { success, error } = useNotificationStore();
  
  return (data: Blob, filename: string) => {
    try {
      const url = window.URL.createObjectURL(data);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      success('Download Started', `${filename} is being downloaded`);
    } catch (err) {
      error('Download Failed', 'Failed to download the file');
    }
  };
};

// Custom hook for handling file uploads
export const useFileUpload = () => {
  const { addFile, updateFileProgress, completeFileUpload } = useConversionStore();
  const { success, error } = useNotificationStore();
  
  const uploadFile = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const fileUpload = addFile(file);
      
      // Simulate file upload progress
      let progress = 0;
      const interval = setInterval(() => {
        progress += Math.random() * 20;
        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
          completeFileUpload(fileUpload.id);
          success('Upload Complete', `${file.name} uploaded successfully`);
          resolve(fileUpload.id);
        } else {
          updateFileProgress(fileUpload.id, progress);
        }
      }, 200);
      
      // Simulate occasional upload failure
      if (Math.random() < 0.05) { // 5% chance of failure
        setTimeout(() => {
          clearInterval(interval);
          error('Upload Failed', `Failed to upload ${file.name}`);
          reject(new Error('Upload failed'));
        }, 1000);
      }
    });
  };
  
  return { uploadFile };
};