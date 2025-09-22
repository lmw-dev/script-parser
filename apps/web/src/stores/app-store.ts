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

  startProcessing: (data) => set({
    requestData: data,
    appState: 'PROCESSING',
    error: null,
  }),

  setSuccess: (result) => set({
    resultData: result,
    appState: 'SUCCESS',
  }),

  setError: (errorMsg) => set({
    error: errorMsg,
    appState: 'ERROR',
  }),

  reset: () => set({
    appState: 'IDLE',
    requestData: null,
    resultData: null,
    error: null,
  }),
}));
