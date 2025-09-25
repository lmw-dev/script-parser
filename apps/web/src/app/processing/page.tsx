"use client"

import { useEffect, useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { useAppStore } from "@/stores/app-store"
import { parseVideo } from "@/lib/api-client"
import { ProcessingSection } from "@/components/sections/ProcessingSection"
import { useProgressAnimation } from "@/lib/progress-algorithm"
import { AlertTriangle } from "lucide-react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

export default function ProcessingPage() {
  const router = useRouter()
  const appState = useAppStore((state) => state.appState)
  const requestData = useAppStore((state) => state.requestData)
  const errorMessage = useAppStore((state) => state.error)
  const setSuccess = useAppStore((state) => state.setSuccess)
  const setError = useAppStore((state) => state.setError)
  const [apiCompleted, setApiCompleted] = useState(false)
  const requestSent = useRef(false)

  const handleCompletion = () => {
    const finalState = useAppStore.getState()
    if (finalState.appState === 'SUCCESS') {
      router.push('/result')
    }
    // Error case is handled by the AlertDialog below
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

      if (requestSent.current) {
        return
      }
      requestSent.current = true

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

  const handleReturnHome = () => {
    router.push("/")
  }

  return (
    <main className="flex-grow flex flex-col items-center justify-center p-6">
      {appState === 'ERROR' ? (
        <AlertDialog open={true}>
          <AlertDialogContent className="max-w-lg">
            <AlertDialogHeader className="flex flex-col items-center text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center">
                <AlertTriangle className="w-10 h-10 text-destructive" />
              </div>
              <div className="space-y-2">
                <AlertDialogTitle className="text-2xl font-bold">处理失败</AlertDialogTitle>
                <AlertDialogDescription className="text-base text-muted-foreground">
                  {errorMessage || "发生未知错误，请稍后重试或联系技术支持。"}
                </AlertDialogDescription>
              </div>
            </AlertDialogHeader>
            <AlertDialogFooter className="mt-6">
              <AlertDialogAction onClick={handleReturnHome} className="w-full h-12 text-lg">
                返回首页
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      ) : (
        <ProcessingSection
          step={currentStage}
          steps={[]}
          progress={progress}
          stageName={stageName}
        />
      )}
    </main>
  )
}