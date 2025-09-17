/**
 * ErrorSection component - displays error states
 * Based on TOM-318 specification
 */

"use client"

import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { AlertTriangle, RefreshCw, XCircle } from "lucide-react"
import type { ErrorSectionProps } from "@/types/script-parser.types"

export function ErrorSection({ error, onReset }: ErrorSectionProps) {
  return (
    <div className="text-center space-y-8 max-w-lg mx-auto">
      <div className="space-y-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-20 h-20 rounded-full bg-destructive/20 animate-pulse" />
          </div>
          <div className="relative flex items-center justify-center">
            <div className="w-12 h-12 rounded-full bg-destructive flex items-center justify-center glow-effect">
              <XCircle className="h-6 w-6 text-white" />
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <h2 className="text-3xl font-bold text-destructive">处理失败</h2>
          <p className="text-lg text-muted-foreground">很抱歉，处理过程中遇到了问题</p>
        </div>
      </div>

      <Alert className="bg-white/80 backdrop-blur-sm border border-destructive/50 bg-destructive/5 shadow-lg">
        <AlertTriangle className="h-5 w-5 text-destructive" />
        <AlertDescription className="text-left text-base">{error || "处理过程中出现了错误，请重试"}</AlertDescription>
      </Alert>

      <Button onClick={onReset} className="bg-primary hover:bg-primary/90 text-white px-8 py-3">
        <RefreshCw className="h-4 w-4 mr-2" />
        重新开始
      </Button>
    </div>
  )
}
