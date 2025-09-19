"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useToast } from "@/hooks/use-toast"
import { useAnalysisStore } from "@/stores/analysis-store"
import { ResultSection } from "@/components/sections/ResultSection"

export default function ResultPage() {
  const router = useRouter()
  const { toast } = useToast()
  const { result, clearAll } = useAnalysisStore()

  // Redirect to home if no result
  useEffect(() => {
    if (!result) {
      router.push('/')
      return
    }
  }, [result, router])

  // Handle reset - go back to home
  const handleReset = () => {
    clearAll()
    router.push('/')
  }

  // Handle copy
  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "已复制到剪贴板",
      duration: 2000,
    })
  }

  // Handle download
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

  // Show loading if no result yet
  if (!result) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="p-8">
        <ResultSection 
          result={result} 
          onReset={handleReset} 
          onCopy={handleCopy} 
          onDownload={handleDownload} 
        />
      </div>
    </div>
  )
}
