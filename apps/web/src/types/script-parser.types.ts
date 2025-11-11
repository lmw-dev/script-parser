/**
 * Core type definitions for the Script Parser application
 * Following TypeScript best practices with strict type safety
 */

// State machine types based on TOM-318 specification
export type AppState = "IDLE" | "INPUT_VALID" | "PROCESSING" | "SUCCESS" | "ERROR"

// Input types for flexible video input
export type InputType = "url" | "file"

// Analysis mode types (V3.0 - TOM-489)
export type AnalysisMode = "general" | "tech" | ""

// V2.0 通用叙事分析结果结构（保留向后兼容）
export type AnalysisResult = {
  readonly raw_transcript: string
  readonly cleaned_transcript: string
  readonly analysis: {
    readonly hook: string
    readonly core: string
    readonly cta: string
    readonly key_quotes?: readonly string[] // V3.0: 金句提炼
  }
}

/**
 * V2.0 通用叙事输出结构（明确标识）
 * @description 用于"通用叙事分析"模式的输出，包含钩子、核心、CTA
 */
export type V2NarrativeOutput = AnalysisResult & {
  readonly schema_type?: 'v2_narrative' // 可选，用于明确标识
}

/**
 * V3.0 科技评测输出结构
 * @description 用于"科技产品评测"模式的输出，包含产品参数、卖点、价格、评价
 */
export type V3TechSpecOutput = {
  readonly schema_type: 'v3_tech_spec'
  readonly product_parameters: ReadonlyArray<{
    readonly parameter: string
    readonly value: string
  }>
  readonly selling_points: ReadonlyArray<{
    readonly point: string
    readonly context_snippet: string
  }>
  readonly pricing_info: ReadonlyArray<{
    readonly product: string
    readonly price: string
    readonly context_snippet: string
  }>
  readonly subjective_evaluation: {
    readonly pros: readonly string[]
    readonly cons: readonly string[]
  }
}

/**
 * 动态分析结果联合类型
 * @description 后端可能返回的两种结构：V2.0 通用叙事 或 V3.0 科技评测
 */
export type DynamicAnalysisResult = V2NarrativeOutput | V3TechSpecOutput

// This represents the nested `llm_analysis` object from the backend (V3.0).
export type ApiAnalysisResult = {
  readonly hook: string
  readonly core: string
  readonly cta: string
  readonly key_quotes?: readonly string[] // V3.0: 金句提炼
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
  readonly analysisMode: AnalysisMode // V3.0 - TOM-489
  readonly onInputChange: (value: string) => void
  readonly onFileSelect: (file: File | null) => void
  readonly onAnalysisModeChange: (mode: AnalysisMode) => void // V3.0 - TOM-489
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
  readonly result: DynamicAnalysisResult // V3.0 - TOM-494: 支持动态结构
  readonly onReset: () => void
}

export type ErrorSectionProps = {
  readonly error: string
  readonly onReset: () => void
}