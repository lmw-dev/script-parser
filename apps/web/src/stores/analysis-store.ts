/**
 * Zustand store for analysis state management
 * Handles data flow between pages in the multi-page architecture
 */

import { create } from 'zustand'
import type { VideoParseRequest, AnalysisResult } from '@/types/script-parser.types'

interface AnalysisStore {
  // Input data from home page
  inputData: VideoParseRequest | null
  
  // Analysis result from processing
  result: AnalysisResult | null
  
  // Error state
  error: string | null
  
  // Actions
  setInputData: (data: VideoParseRequest) => void
  setResult: (result: AnalysisResult) => void
  setError: (error: string | null) => void
  clearAll: () => void
}

export const useAnalysisStore = create<AnalysisStore>((set) => ({
  // Initial state
  inputData: null,
  result: null,
  error: null,
  
  // Actions
  setInputData: (data) => set({ inputData: data, error: null }),
  setResult: (result) => set({ result, error: null }),
  setError: (error) => set({ error, result: null }),
  clearAll: () => set({ inputData: null, result: null, error: null }),
}))
