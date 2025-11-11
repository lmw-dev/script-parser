import { create } from 'zustand';
import type { AppState, VideoParseRequest, AnalysisResult, AnalysisMode } from '@/types/script-parser.types';

// Zustand Store 接口
export interface AppStore {
  // State
  appState: AppState;
  requestData: VideoParseRequest | null;
  resultData: AnalysisResult | null;
  error: string | null;
  analysisMode: AnalysisMode; // V3.0 - TOM-489

  // Actions
  startProcessing: (data: VideoParseRequest) => void;
  setSuccess: (result: AnalysisResult) => void;
  setError: (errorMsg: string) => void;
  reset: () => void;
  setAnalysisMode: (mode: AnalysisMode) => void; // V3.0 - TOM-489
  resetPartial: () => void; // V3.0 - TOM-489: Reset all except analysisMode
}

export const useAppStore = create<AppStore>((set) => ({
  appState: 'IDLE',
  requestData: null,
  resultData: null,
  error: null,
  analysisMode: '', // V3.0 - TOM-489: Initial state is empty (user must select)

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
    analysisMode: '', // V3.0 - TOM-489: Full reset includes analysisMode
  }),

  // V3.0 - TOM-489: Set analysis mode
  setAnalysisMode: (mode) => set({
    analysisMode: mode,
  }),

  // V3.0 - TOM-489: Partial reset (preserve analysisMode for "smart reset")
  resetPartial: () => set((state) => ({
    appState: 'IDLE',
    requestData: null,
    resultData: null,
    error: null,
    // Preserve analysisMode from current state
    analysisMode: state.analysisMode,
  })),
}));
