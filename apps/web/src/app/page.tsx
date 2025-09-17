"use client"

import { useState } from "react"
import { useToast } from "@/hooks/use-toast"
import { InputSection } from "@/components/sections/InputSection"
import { ProcessingSection } from "@/components/sections/ProcessingSection"
import { ResultSection } from "@/components/sections/ResultSection"
import { ErrorSection } from "@/components/sections/ErrorSection"
import { mockParseVideo } from "@/lib/api-client"
import { extractAndValidateUrl, validateVideoFile } from "@/lib/validation"
import type { AppState, AnalysisResult, VideoParseRequest } from "@/types/script-parser.types"
import { Sparkles, FileText, Zap } from "lucide-react"

export default function ScriptParser() {
  const [state, setState] = useState<AppState>("IDLE")
  const [processingStep, setProcessingStep] = useState(1)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState("")
  
  // InputSection controlled state
  const [inputValue, setInputValue] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  
  const { toast } = useToast()

  const processingSteps = [
    "(1/3) 正在安全上传并解析视频...",
    "(2/3) 正在调用ASR服务，提取高质量逐字稿...",
    "(3/3) 正在调用LLM，进行AI结构化分析...",
  ] as const

  // Handle input change with URL extraction and validation
  const handleInputChange = (value: string) => {
    setInputValue(value)
    
    // Update state based on input validation
    if (value.trim() === "") {
      setState("IDLE")
      setError("")
      return
    }

    // Try to extract and validate URL from the input text
    const validationResult = extractAndValidateUrl(value)
    
    if (validationResult.isValid) {
      setState("INPUT_VALID")
      setError("")
    } else {
      setState("IDLE")
      // Don't show error immediately, only when user tries to submit
    }
  }

  // Handle file selection - uses the exported logic function
  const handleFileSelect = (file: File | null) => {
    handleFileChangeLogic(file, {
      setAppState: setState,
      setSelectedFile,
      setInputValue,
      setError,
    })
  }

  // Handle form submission
  const handleSubmit = async () => {
    setError("")
    
    // Prepare data for submission
    let data: VideoParseRequest
    
    if (selectedFile) {
      data = { file: selectedFile }
    } else if (inputValue.trim()) {
      const validationResult = extractAndValidateUrl(inputValue)
      
      if (validationResult.isValid && validationResult.extractedUrl) {
        data = { url: validationResult.extractedUrl }
      } else {
        setState("ERROR")
        setError(validationResult.error || "请输入有效的视频链接")
        return
      }
    } else {
      setState("ERROR")
      setError("请输入视频链接或选择文件")
      return
    }

    // Start processing
    setState("PROCESSING")
    setProcessingStep(1)

    try {
      await new Promise((resolve) => setTimeout(resolve, 1500))
      setProcessingStep(2)

      await new Promise((resolve) => setTimeout(resolve, 1500))
      setProcessingStep(3)

      await new Promise((resolve) => setTimeout(resolve, 1500))

      const response = await mockParseVideo(data)

      if (response.success && response.result) {
        setResult(response.result)
        setState("SUCCESS")
      } else {
        throw new Error(response.message || "Analysis failed")
      }
    } catch (err) {
      console.error("[v0] Analysis error:", err)
      setState("ERROR")
      setError("分析过程中出现错误，请重试")
    }
  }

  const handleReset = () => {
    setState("IDLE")
    setResult(null)
    setError("")
    setProcessingStep(1)
    // Reset InputSection state
    setInputValue("")
    setSelectedFile(null)
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "已复制到剪贴板",
      duration: 2000,
    })
  }

  const handleDownload = () => {
    if (!result) return

    const markdown = `# 脚本分析结果

## 完整逐字稿
${result.transcript}

## AI 结构化分析

### 🚀 钩子 (Hook)
${result.analysis.hook}

### 💡 核心 (Core)
${result.analysis.core}

### 🎯 行动号召 (CTA)
${result.analysis.cta}
`

    const blob = new Blob([markdown], { type: "text/markdown" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "script-analysis.md"
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="h-14 bg-primary border-b border-primary/20 flex items-center justify-between px-6">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-white/20 rounded flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="text-white font-semibold text-sm">AI 脚本快拆</span>
            <span className="text-white/60 text-xs">by v0</span>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-3 py-1.5 bg-black/30 hover:bg-black/40 text-white text-xs font-medium rounded-md transition-colors border border-white/10">
            开始使用
          </button>
          <button className="px-3 py-1.5 bg-white text-primary text-xs font-medium rounded-md hover:bg-white/90 transition-colors">
            立即体验
          </button>
        </div>
      </div>

      <div className="h-[calc(100vh-3.5rem)] flex">
        {(state === "IDLE" || state === "INPUT_VALID") && (
          <>
            <div className="w-2/5 bg-gradient-to-br from-primary/5 to-primary/10 border-r border-border flex flex-col justify-center px-12">
              <div className="space-y-8">
                <div className="space-y-6">
                  <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20">
                    <div className="w-1.5 h-1.5 bg-primary rounded-full" />
                    <span className="text-xs font-medium text-foreground/70 uppercase tracking-wide">AI Analysis</span>
                  </div>
                  <h1 className="text-4xl lg:text-5xl font-bold text-gradient-linear tracking-tight leading-tight">
                    AI 脚本快拆
                  </h1>
                  <p className="text-lg text-muted-foreground leading-relaxed">
                    专业级视频脚本分析工具，一键提取逐字稿并进行AI结构化分析
                  </p>
                </div>

                <div className="space-y-6">
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Sparkles className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground mb-1">AI 智能分析</h3>
                      <p className="text-sm text-muted-foreground">先进的AI算法，精准提取脚本结构</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                      <FileText className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground mb-1">多格式支持</h3>
                      <p className="text-sm text-muted-foreground">支持主流视频平台链接和本地文件</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Zap className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground mb-1">快速处理</h3>
                      <p className="text-sm text-muted-foreground">秒级响应，高效完成分析任务</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex-1 flex items-center justify-center px-12">
              <InputSection 
                currentState={state}
                inputValue={inputValue}
                selectedFile={selectedFile}
                onInputChange={handleInputChange}
                onFileSelect={handleFileSelect}
                onSubmit={handleSubmit}
                error={error}
              />
            </div>
          </>
        )}

        {state === "PROCESSING" && (
          <div className="flex-1 flex items-center justify-center">
            <ProcessingSection step={processingStep} steps={processingSteps} />
          </div>
        )}

        {state === "SUCCESS" && result && (
          <div className="flex-1 p-8 overflow-auto">
            <ResultSection result={result} onReset={handleReset} onCopy={handleCopy} onDownload={handleDownload} />
          </div>
        )}

        {state === "ERROR" && (
          <div className="flex-1 flex items-center justify-center">
            <ErrorSection error={error} onReset={handleReset} />
          </div>
        )}
      </div>
    </div>
  )
}

// Export the file handling logic function for testing
export const handleFileChangeLogic = (
  file: File | null,
  context: {
    setAppState: (state: AppState) => void
    setSelectedFile: (file: File | null) => void
    setInputValue: (value: string) => void
    setError: (error: string) => void
  },
  validateFn = validateVideoFile
) => {
  // Handle null file (user cleared selection)
  if (!file) {
    context.setSelectedFile(null)
    context.setAppState("IDLE")
    context.setError("")
    return
  }

  // Validate the selected file
  const validationResult = validateFn(file)
  
  if (validationResult.isValid) {
    // File is valid
    context.setAppState("INPUT_VALID")
    context.setSelectedFile(file)
    context.setInputValue("") // Clear URL input when file is selected
    context.setError("")
  } else {
    // File is invalid
    context.setAppState("ERROR")
    context.setSelectedFile(null)
    context.setError(validationResult.error || "文件验证失败")
  }
}
