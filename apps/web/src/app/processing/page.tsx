"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAppStore } from "@/stores/app-store"
import { parseVideo } from "@/lib/api-client"
import { ProcessingSection } from "@/components/sections/ProcessingSection"
import { useProgressAnimation } from "@/lib/progress-algorithm"

export default function ProcessingPage() {
  const router = useRouter()
  const requestData = useAppStore((state) => state.requestData)
  const setSuccess = useAppStore((state) => state.setSuccess)
  const setError = useAppStore((state) => state.setError)
  const [apiCompleted, setApiCompleted] = useState(false)

  const handleCompletion = () => {
    const finalState = useAppStore.getState()
    if (finalState.appState === 'SUCCESS') {
      router.push('/result')
    } else if (finalState.appState === 'ERROR') {
      router.push('/error')
    }
  }

  const { progress, currentStage, stageName } = useProgressAnimation(
    handleCompletion,
    apiCompleted
  )

  useEffect(() => {
    const processRequest = async () => {
      if (!requestData) {
        router.replace("/")
        return
      }

      try {
        const result = await parseVideo(requestData)
        setSuccess(result)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "An unknown error occurred."
        setError(errorMessage)
      } finally {
        setApiCompleted(true)
      }
    }

    processRequest()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestData, setSuccess, setError, router])

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-background">
      <ProcessingSection
        step={currentStage}
        steps={[]}
        progress={progress}
        stageName={stageName}
      />
    </main>
  )
}