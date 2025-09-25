/**
 * ProcessingSection component - displays processing progress
 * Based on TOM-318 specification
 */

"use client"

import { Progress } from "@/components/ui/progress"
import { Brain, FileText, Sparkles } from "lucide-react"
import type { ProcessingSectionProps } from "@/types/script-parser.types"

interface EnhancedProcessingSectionProps extends ProcessingSectionProps {
  progress?: number
  stageName?: string
}

export function ProcessingSection({ 
  step, 
  steps, 
  progress: customProgress, 
  stageName 
}: EnhancedProcessingSectionProps) {
  // Use custom progress if provided, otherwise calculate from step
  const progress = customProgress !== undefined ? customProgress : (step / steps.length) * 100
  const displayStageName = stageName || steps[step - 1]

  const stepIcons = [
    <FileText key="1" className="h-5 w-5" />,
    <Brain key="2" className="h-5 w-5" />,
    <Sparkles key="3" className="h-5 w-5" />,
  ]

  return (
    <div className="text-center space-y-8 w-full max-w-3xl mx-auto p-4">
      <div className="space-y-6">
        <div className="relative flex items-center justify-center h-32">
          {/* Outer ring */}
          <div
            className="absolute w-24 h-24 md:w-32 md:h-32 rounded-full border-2 border-cyan-400/30 animate-spin"
            style={{ animationDuration: "3s" }}
          />
          {/* Middle ring */}
          <div
            className="absolute w-20 h-20 md:w-24 md:h-24 rounded-full border-2 border-purple-400/50 animate-spin"
            style={{ animationDuration: "2s", animationDirection: "reverse" }}
          />
          {/* Inner pulsing core */}
          <div className="relative w-12 h-12 md:w-16 md:h-16 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 flex items-center justify-center animate-pulse shadow-2xl shadow-cyan-400/50">
            <div className="w-10 h-10 md:w-12 md:h-12 rounded-full bg-gradient-to-r from-purple-600 to-cyan-600 flex items-center justify-center">
              <Brain className="h-5 w-5 md:h-6 md:w-6 text-white animate-pulse" />
            </div>
          </div>
          {/* Floating particles (some hidden on mobile for clarity) */}
          <div
            className="absolute w-2 h-2 bg-cyan-400 rounded-full animate-ping"
            style={{ top: "20%", left: "80%", animationDelay: "0s" }}
          />
          <div
            className="absolute w-1.5 h-1.5 bg-purple-400 rounded-full animate-ping hidden md:block"
            style={{ top: "70%", left: "20%", animationDelay: "1s" }}
          />
          <div
            className="absolute w-1 h-1 bg-cyan-300 rounded-full animate-ping"
            style={{ top: "30%", left: "15%", animationDelay: "2s" }}
          />
        </div>

        <div className="space-y-1">
          <h2 className="text-2xl md:text-3xl font-bold text-gradient">AI 正在分析中</h2>
          <p className="text-base md:text-lg text-muted-foreground">请稍候，我们的AI正在为您解析视频内容</p>
        </div>
      </div>

      <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 shadow-lg hover:shadow-xl transition-all duration-300 p-6 md:p-8 rounded-xl space-y-6">
        <div className="space-y-4">
          <Progress value={progress} className="w-full h-3 bg-slate-200" />
          <div className="flex items-center justify-center space-x-3 text-primary">
            {stepIcons[step - 1]}
            <p className="text-sm md:text-base font-medium text-center">{displayStageName}</p>
          </div>
        </div>

        {steps && steps.length > 0 && (
          <div className="flex justify-center space-x-4">
            {steps.map((_, index) => (
              <div
                key={index}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  index < step
                    ? "bg-cyan-400 shadow-lg shadow-cyan-400/50"
                    : index === step - 1
                      ? "bg-cyan-400 animate-pulse shadow-lg shadow-cyan-400/50"
                      : "bg-slate-600"
                }`}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
