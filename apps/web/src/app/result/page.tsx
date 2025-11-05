"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAppStore } from "@/stores/app-store"
import { ResultSection } from "@/components/sections/ResultSection"
import { ErrorSection } from "@/components/sections/ErrorSection"
import { DonationSection } from "@/components/feature/DonationSection"
import { EmailSubscriptionForm } from "@/components/feature/EmailSubscriptionForm"

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
      <main className="flex-grow flex flex-col items-center w-full bg-gradient-to-b from-background to-muted/5">
        {/* Results Content - Full Width on Web */}
        <div className="w-full px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <ResultSection
            result={resultData}
            onReset={handleReset}
          />
        </div>

        {/* Divider Section - More Compact */}
        <div className="w-full border-t border-border/30 bg-muted/10">
          <div className="mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
            {/* Donation Section */}
            {enableDonation && (
              <div className="space-y-3">
                <div className="text-center mb-6">
                  <h2 className="text-xl md:text-2xl font-bold text-foreground mb-1">觉得有帮助？</h2>
                  <p className="text-xs md:text-sm text-muted-foreground">支持我们继续打造更好的工具</p>
                </div>
                <DonationSection
                  wechatQrPath="/wechat_donate_qr.png"
                  alipayQrPath="/alipay_donate_qr.png"
                />
              </div>
            )}

            {/* Email Subscription Section */}
            <div className="space-y-3">
              <div className="text-center mb-6">
                <h2 className="text-xl md:text-2xl font-bold text-foreground mb-1">保持关注</h2>
                <p className="text-xs md:text-sm text-muted-foreground">获取最新功能和更新通知</p>
              </div>
              <EmailSubscriptionForm />
            </div>
          </div>
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
