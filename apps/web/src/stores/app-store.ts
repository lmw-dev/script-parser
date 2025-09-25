import { create } from 'zustand';
import type { AppState, VideoParseRequest, AnalysisResult } from '@/types/script-parser.types';

// Zustand Store 接口
export interface AppStore {
  // State
  appState: AppState;
  requestData: VideoParseRequest | null;
  resultData: AnalysisResult | null;
  error: string | null;

  // Actions
  startProcessing: (data: VideoParseRequest) => void;
  setSuccess: (result: AnalysisResult) => void;
  setError: (errorMsg: string) => void;
  reset: () => void;
}

export const useAppStore = create<AppStore>((set) => ({
  appState: 'IDLE',
  requestData: null,
  resultData: null,
  error: null,

  startProcessing: (requestData) => set({
    requestData,
    appState: 'PROCESSING',
    error: null,
  }),

  setSuccess: (resultData) => set({
    resultData,
    appState: 'SUCCESS',
  }),

  setError: (error) => set({
    error,
    appState: 'ERROR',
  }),

  reset: () => set({
    appState: 'IDLE',
    requestData: null,
    resultData: null,
    error: null,
  }),
}));
