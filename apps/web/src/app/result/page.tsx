"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAppStore } from "@/stores/app-store"
import { ResultSection } from "@/components/sections/ResultSection"
import { ErrorSection } from "@/components/sections/ErrorSection"

export default function ResultPage() {
  const router = useRouter()
  const resultData = useAppStore((state) => state.resultData)
  const error = useAppStore((state) => state.error)
  const appState = useAppStore((state) => state.appState)
  const reset = useAppStore((state) => state.reset)

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



  if (appState === "ERROR" && error) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-background">
        <ErrorSection error={error} onReset={handleReset} />
      </main>
    )
  }

  if (appState === "SUCCESS" && resultData) {
    return (
      <main className="flex-grow flex flex-col items-center justify-center p-6">
        <ResultSection
          result={resultData}
          onReset={handleReset}
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
