"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAppStore } from "@/stores/app-store"
import { ResultSection } from "@/components/sections/ResultSection"
import { ErrorSection } from "@/components/sections/ErrorSection"
import { DonationSection } from "@/components/feature/DonationSection"

export default function ResultPage() {
  const router = useRouter()
  const resultData = useAppStore((state) => state.resultData)
  const error = useAppStore((state) => state.error)
  const appState = useAppStore((state) => state.appState)
  const reset = useAppStore((state) => state.reset)
  const enableDonation = process.env.NEXT_PUBLIC_ENABLE_DONATION === 'true'

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
        <div className="w-full max-w-4xl space-y-8">
          <ResultSection
            result={resultData}
            onReset={handleReset}
          />
          {enableDonation && (
            <div className="mt-12">
              <DonationSection
                wechatQrPath="/wechat_donate_qr.png"
                alipayQrPath="/alipay_donate_qr.png"
              />
            </div>
          )}
        </div>
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
