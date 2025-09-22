"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAppStore } from "@/stores/app-store"
import { useToast } from "@/hooks/use-toast"
import { ResultSection } from "@/components/sections/ResultSection"
import { ErrorSection } from "@/components/sections/ErrorSection"

export default function ResultPage() {
  const router = useRouter()
  const { toast } = useToast()
  const { resultData, error, appState, reset } = useAppStore()

  useEffect(() => {
    // Redirect if user lands here without going through the process
    if (appState !== "SUCCESS" && appState !== "ERROR") {
      router.replace("/")
    }
  }, [appState, router])

  const handleReset = () => {
    reset()
    router.push("/")
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "已复制到剪贴板",
      duration: 2000,
    })
  }

  const handleDownload = () => {
    if (!resultData) return

    const markdownContent = `
# AI 脚本分析结果

## 逐字稿

${resultData.transcript}

---

## AI 结构化分析

### 🚀 钩子 (Hook)
${resultData.analysis.hook}

### 💡 核心 (Core)
${resultData.analysis.core}

### 🎯 行动号召 (CTA)
${resultData.analysis.cta}
`
    const blob = new Blob([markdownContent.trim()], { type: "text/markdown" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "script-analysis-result.md"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast({
      title: "结果已开始下载",
      description: "文件将保存为 script-analysis-result.md",
      duration: 3000,
    })
  }

  if (appState === "ERROR" && error) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-background">
        <ErrorSection error={error} onReset={handleReset} />
      </main>
    )
  }

  if (appState === "SUCCESS" && resultData) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-background">
        <ResultSection
          result={resultData}
          onReset={handleReset}
          onCopy={handleCopy}
          onDownload={handleDownload}
        />
      </main>
    )
  }

  // Render a loading state or redirect
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-background">
      <p>正在加载结果...</p>
    </main>
  )
}
