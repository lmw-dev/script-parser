"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAnalysisStore } from "@/stores/analysis-store"
import { parseVideo } from "@/lib/api-client"
import { useProgressAnimation } from "@/lib/progress-algorithm"
import { ProcessingSection } from "@/components/sections/ProcessingSection"
import { ErrorSection } from "@/components/sections/ErrorSection"
import type { AnalysisResult, ApiAnalysisResult } from "@/types/script-parser.types"

export default function ProcessingPage() {
  const router = useRouter()
  const { inputData, setResult, setError, clearAll } = useAnalysisStore()
  const [apiCompleted, setApiCompleted] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)

  // Redirect to home if no input data
  useEffect(() => {
    if (!inputData) {
      router.push('/')
      return
    }
  }, [inputData, router])

  // Handle API completion
  const handleProgressComplete = () => {
    if (apiCompleted) {
      router.push('/result')
    }
  }

  // Progress animation hook
  const { progress, currentStage, stageName } = useProgressAnimation(
    handleProgressComplete,
    apiCompleted
  )

  // Start API call
  useEffect(() => {
    if (!inputData) return

    const callAPI = async () => {
      try {
        // Call the API
        const result: ApiAnalysisResult = await parseVideo(inputData)

        // Store result
        const analysisResult: AnalysisResult = {
          transcript: "API逐字稿内容将在后端实现后显示",
          analysis: {
            hook: result.hook,
            core: result.core,
            cta: result.cta
          }
        }
        
        setResult(analysisResult)
        setApiCompleted(true)
      } catch (err) {
        console.error("[API] Analysis error:", err)
        const errorMessage = err instanceof Error ? err.message : "分析过程中出现错误，请重试"
        setApiError(errorMessage)
        setError(errorMessage)
      }
    }

    // Start API call after a short delay
    const timer = setTimeout(callAPI, 1000)
    return () => clearTimeout(timer)
  }, [inputData, setResult, setError])

  // Handle reset
  const handleReset = () => {
    clearAll()
    router.push('/')
  }

  // Show error if API failed
  if (apiError) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <ErrorSection error={apiError} onReset={handleReset} />
      </div>
    )
  }

  // Show processing with progress
  const processingSteps = [
    "(1/3) 正在安全上传并解析视频...",
    "(2/3) 正在调用ASR服务，提取高质量逐字稿...",
    "(3/3) 正在调用LLM，进行AI结构化分析...",
  ] as const

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <ProcessingSection 
        step={currentStage} 
        steps={processingSteps}
        progress={progress}
        stageName={stageName}
      />
    </div>
  )
}
