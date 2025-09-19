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
    <div className="text-center space-y-8 max-w-3xl mx-auto">
      <div className="space-y-6">
        <div className="relative flex items-center justify-center">
          {/* Outer ring */}
          <div
            className="absolute w-32 h-32 rounded-full border-2 border-cyan-400/30 animate-spin"
            style={{ animationDuration: "3s" }}
          />
          {/* Middle ring */}
          <div
            className="absolute w-24 h-24 rounded-full border-2 border-purple-400/50 animate-spin"
            style={{ animationDuration: "2s", animationDirection: "reverse" }}
          />
          {/* Inner pulsing core */}
          <div className="relative w-16 h-16 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 flex items-center justify-center animate-pulse shadow-2xl shadow-cyan-400/50">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-600 to-cyan-600 flex items-center justify-center">
              <Brain className="h-6 w-6 text-white animate-pulse" />
            </div>
          </div>
          {/* Floating particles */}
          <div
            className="absolute w-2 h-2 bg-cyan-400 rounded-full animate-ping"
            style={{ top: "20%", left: "80%", animationDelay: "0s" }}
          />
          <div
            className="absolute w-1.5 h-1.5 bg-purple-400 rounded-full animate-ping"
            style={{ top: "70%", left: "20%", animationDelay: "1s" }}
          />
          <div
            className="absolute w-1 h-1 bg-cyan-300 rounded-full animate-ping"
            style={{ top: "30%", left: "15%", animationDelay: "2s" }}
          />
        </div>

        <div className="space-y-2">
          <h2 className="text-3xl font-bold text-gradient">AI 正在分析中</h2>
          <p className="text-lg text-muted-foreground">请稍候，我们的AI正在为您解析视频内容</p>
        </div>
      </div>

      <div className="bg-white/80 backdrop-blur-sm border border-slate-200/60 shadow-lg hover:shadow-xl transition-all duration-300 p-8 rounded-xl space-y-6">
        <div className="space-y-4">
          <Progress value={progress} className="w-full h-3 bg-slate-200" />
          <div className="flex items-center justify-center space-x-3 text-primary">
            {stepIcons[step - 1]}
            <p className="text-base font-medium">{displayStageName}</p>
          </div>
        </div>

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
      </div>
    </div>
  )
}
