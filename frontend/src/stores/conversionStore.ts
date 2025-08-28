import { create } from 'zustand';
import type { 
  ConversionRequest, 
  ConversionResponse, 
  ConversionHistory, 
  FileUpload,
  ConversionStatus
} from '../types';
import { generateId } from '../utils';

interface ConversionState {
  // Current conversion state
  currentConversion: ConversionResponse | null;
  isConverting: boolean;
  conversionProgress: number;
  
  // File upload state
  uploadedFiles: FileUpload[];
  
  // Conversion history
  history: ConversionHistory[];
  
  // UI state
  selectedFormat: string | null;
  conversionOptions: Record<string, any>;
  
  // Actions
  startConversion: (request: ConversionRequest) => Promise<void>;
  updateProgress: (progress: number) => void;
  completeConversion: (result: ConversionResponse) => void;
  failConversion: (error: string) => void;
  
  // File upload actions
  addFile: (file: File) => FileUpload;
  updateFileProgress: (fileId: string, progress: number) => void;
  completeFileUpload: (fileId: string) => void;
  removeFile: (fileId: string) => void;
  clearFiles: () => void;
  
  // History actions
  addToHistory: (conversion: ConversionHistory) => void;
  clearHistory: () => void;
  
  // Settings actions
  setSelectedFormat: (format: string) => void;
  updateConversionOptions: (options: Record<string, any>) => void;
  resetConversionState: () => void;
}

export const useConversionStore = create<ConversionState>((set, get) => ({
  // Initial state
  currentConversion: null,
  isConverting: false,
  conversionProgress: 0,
  uploadedFiles: [],
  history: [],
  selectedFormat: null,
  conversionOptions: {},
  
  // Conversion actions
  startConversion: async (request: ConversionRequest) => {
    set({ 
      isConverting: true, 
      conversionProgress: 0,
      currentConversion: {
        job_id: generateId(),
        status: ConversionStatus.PENDING,
        message: 'Starting conversion...',
      }
    });
    
    // Add to history
    const historyItem: ConversionHistory = {
      id: generateId(),
      job_id: get().currentConversion?.job_id || '',
      input_format: 'auto', // Will be detected from file
      output_format: request.output_format,
      file_name: 'document', // Will be updated with actual filename
      file_size: request.content.length,
      status: ConversionStatus.PENDING,
      created_at: new Date().toISOString(),
    };
    
    get().addToHistory(historyItem);
  },
  
  updateProgress: (progress: number) => {
    set({ conversionProgress: progress });
  },
  
  completeConversion: (result: ConversionResponse) => {
    set({ 
      currentConversion: result,
      isConverting: false,
      conversionProgress: 100
    });
    
    // Update history
    const { history } = get();
    const updatedHistory = history.map(item => 
      item.job_id === result.job_id 
        ? { 
            ...item, 
            status: result.status,
            completed_at: new Date().toISOString(),
            processing_time: result.processing_time
          }
        : item
    );
    
    set({ history: updatedHistory });
  },
  
  failConversion: (error: string) => {
    const { currentConversion } = get();
    if (currentConversion) {
      set({ 
        currentConversion: {
          ...currentConversion,
          status: ConversionStatus.FAILED,
          message: error
        },
        isConverting: false
      });
      
      // Update history
      const { history } = get();
      const updatedHistory = history.map(item => 
        item.job_id === currentConversion.job_id 
          ? { 
              ...item, 
              status: ConversionStatus.FAILED,
              error_message: error,
              completed_at: new Date().toISOString()
            }
          : item
      );
      
      set({ history: updatedHistory });
    }
  },
  
  // File upload actions
  addFile: (file: File) => {
    const fileUpload: FileUpload = {
      id: generateId(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      progress: 0,
      status: 'uploading'
    };
    
    set(state => ({ 
      uploadedFiles: [...state.uploadedFiles, fileUpload] 
    }));
    
    return fileUpload;
  },
  
  updateFileProgress: (fileId: string, progress: number) => {
    set(state => ({
      uploadedFiles: state.uploadedFiles.map(file => 
        file.id === fileId ? { ...file, progress } : file
      )
    }));
  },
  
  completeFileUpload: (fileId: string) => {
    set(state => ({
      uploadedFiles: state.uploadedFiles.map(file => 
        file.id === fileId 
          ? { ...file, progress: 100, status: 'completed' as const }
          : file
      )
    }));
  },
  
  removeFile: (fileId: string) => {
    set(state => ({
      uploadedFiles: state.uploadedFiles.filter(file => file.id !== fileId)
    }));
  },
  
  clearFiles: () => {
    set({ uploadedFiles: [] });
  },
  
  // History actions
  addToHistory: (conversion: ConversionHistory) => {
    set(state => ({ 
      history: [conversion, ...state.history].slice(0, 100) // Keep last 100 conversions
    }));
  },
  
  clearHistory: () => {
    set({ history: [] });
  },
  
  // Settings actions
  setSelectedFormat: (format: string) => {
    set({ selectedFormat: format });
  },
  
  updateConversionOptions: (options: Record<string, any>) => {
    set(state => ({ 
      conversionOptions: { ...state.conversionOptions, ...options }
    }));
  },
  
  resetConversionState: () => {
    set({ 
      currentConversion: null,
      isConverting: false,
      conversionProgress: 0,
      selectedFormat: null,
      conversionOptions: {}
    });
  },
}));