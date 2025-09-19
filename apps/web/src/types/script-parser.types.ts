/**
 * Core type definitions for the Script Parser application
 * Following TypeScript best practices with strict type safety
 */

// State machine types based on TOM-318 specification
export type AppState = "IDLE" | "INPUT_VALID" | "PROCESSING" | "SUCCESS" | "ERROR"

// Input types for flexible video input
export type InputType = "url" | "file"

// Analysis result structure (for display)
export type AnalysisResult = {
  readonly transcript: string
  readonly analysis: {
    readonly hook: string
    readonly core: string
    readonly cta: string
  }
}

// API result structure (from parseVideo function)
export type ApiAnalysisResult = {
  readonly hook: string
  readonly core: string
  readonly cta: string
}

// API request/response types
export type VideoParseRequest = {
  readonly type: 'url' | 'file'
  readonly url: string
  readonly file: File | null
}

export type VideoParseResponse = {
  readonly success: boolean
  readonly message: string
  readonly task_id: string
  readonly result?: AnalysisResult
}

// Component props interfaces
export type InputSectionProps = {
  readonly currentState: AppState
  readonly inputValue: string // Controlled by parent component
  readonly selectedFile: File | null // Controlled by parent component
  readonly onInputChange: (value: string) => void // Controlled by parent component
  readonly onFileSelect: (file: File | null) => void // Controlled by parent component
  readonly onSubmit: () => void // Simplified - no data parameter
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
  readonly onCopy: (text: string) => void
  readonly onDownload: () => void
}

export type ErrorSectionProps = {
  readonly error: string
  readonly onReset: () => void
}
