/**
 * Core type definitions for the Script Parser application
 * Following TypeScript best practices with strict type safety
 */

// State machine types based on TOM-318 specification
export type AppState = "IDLE" | "INPUT_VALID" | "PROCESSING" | "SUCCESS" | "ERROR"

// Input types for flexible video input
export type InputType = "url" | "file"

// This is the final, clean data structure used by the frontend components (V2.2).
export type AnalysisResult = {
  readonly raw_transcript: string
  readonly cleaned_transcript: string
  readonly analysis: {
    readonly hook: string
    readonly core: string
    readonly cta: string
  }
}

// This represents the nested `llm_analysis` object from the backend.
export type ApiAnalysisResult = {
  readonly hook: string
  readonly core: string
  readonly cta: string
}

// This represents the structure of the `data` object in the backend response (V2.2).
export type BackendData = {
  readonly raw_transcript: string;
  readonly cleaned_transcript: string;
  readonly analysis: {
    readonly llm_analysis: ApiAnalysisResult;
    // other potential fields from the backend
    readonly video_info?: any;
    readonly file_info?: any;
  };
};

// API request/response types
export type VideoParseRequest = {
  readonly type: 'url' | 'file'
  readonly url: string
  readonly file: File | null
}

// This now accurately reflects the JSON response from the Python backend.
export type VideoParseResponse = {
  readonly success: boolean
  readonly code: number
  readonly message?: string
  readonly data?: BackendData
}

// Component props interfaces
export type InputSectionProps = {
  readonly currentState: AppState
  readonly inputValue: string
  readonly selectedFile: File | null
  readonly onInputChange: (value: string) => void
  readonly onFileSelect: (file: File | null) => void
  readonly onSubmit: () => void
  readonly error?: string
}

export type ProcessingSectionProps = {
  readonly step: number
  readonly steps: ReadonlyArray<string>
  readonly progress?: number
  readonly stageName?: string
}

export type ResultSectionProps = {
  readonly result: AnalysisResult
  readonly onReset: () => void
}

export type ErrorSectionProps = {
  readonly error: string
  readonly onReset: () => void
}