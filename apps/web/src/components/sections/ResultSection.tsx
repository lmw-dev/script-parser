/**
 * ResultSection component - displays analysis results
 * Based on TOM-318, TOM-346 and TOM-347 specifications
 */

"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Copy, Download, RefreshCw, CheckCircle, FileText, Target, Zap } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { copyToClipboard, downloadAsMarkdown } from "@/lib/utils"
import type { AnalysisResult } from "@/types/script-parser.types"

// Update props to remove onCopy and onDownload as they are now handled internally
export type ResultSectionProps = {
  readonly result: AnalysisResult
  readonly onReset: () => void
}

export function ResultSection({ result, onReset }: ResultSectionProps) {
  const { toast } = useToast()

  const handleCopy = (textToCopy: string, type: string) => {
    try {
      const success = copyToClipboard(textToCopy)
      if (success) {
        toast({
          title: "复制成功！",
          description: `${type} 已复制到您的剪贴板。`,
        })
      } else {
        throw new Error("copyToClipboard returned false")
      }
    } catch (error) {
      toast({
        title: "复制失败",
        description: "无法访问剪贴板，请检查浏览器权限。",
        variant: "destructive",
      })
    }
  }

  const handleDownload = () => {
    try {
      downloadAsMarkdown(result)
      toast({
        title: "结果已开始下载",
        description: "文件将保存为 script-analysis.md",
        duration: 3000,
      })
    } catch (error) {
      toast({
        title: "下载失败",
        description: "无法生成下载文件，请稍后重试。",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="space-y-8">
      <div className="text-center space-y-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-20 h-20 rounded-full bg-green-500/20 animate-pulse" />
          </div>
          <div className="relative flex items-center justify-center">
            <div className="w-12 h-12 rounded-full bg-green-500 flex items-center justify-center glow-effect-strong">
              <CheckCircle className="h-6 w-6 text-white" />
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <h2 className="text-4xl font-bold text-gradient">分析完成</h2>
          <p className="text-lg text-muted-foreground">AI已为您完成脚本结构化分析</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="bg-white/80 backdrop-blur-sm border border-slate-200/60 shadow-lg hover:shadow-xl transition-all duration-300">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center justify-between text-xl">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-primary" />
                <span>完整逐字稿</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleCopy(result.transcript, "完整逐字稿")}
                className="border-primary/20 bg-transparent hover:bg-primary/10"
              >
                <Copy className="h-4 w-4" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="code-block p-4 rounded-lg max-h-96 overflow-y-auto">
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">{result.transcript}</p>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card className="bg-white/80 backdrop-blur-sm border border-slate-200/60 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center justify-between text-lg">
                <div className="flex items-center space-x-2">
                  <Zap className="h-5 w-5 text-yellow-500" />
                  <span>🚀 钩子 (Hook)</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCopy(result.analysis.hook, "钩子")}
                  className="border-primary/20 bg-transparent hover:bg-primary/10"
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-foreground/90">{result.analysis.hook}</p>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border border-slate-200/60 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center justify-between text-lg">
                <div className="flex items-center space-x-2">
                  <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                    <span className="text-xs text-white">💡</span>
                  </div>
                  <span>核心 (Core)</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCopy(result.analysis.core, "核心")}
                  className="border-primary/20 bg-transparent hover:bg-primary/10"
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-foreground/90">{result.analysis.core}</p>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border border-slate-200/60 shadow-lg hover:shadow-xl transition-all duration-300">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center justify-between text-lg">
                <div className="flex items-center space-x-2">
                  <Target className="h-5 w-5 text-green-500" />
                  <span>🎯 行动号召 (CTA)</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCopy(result.analysis.cta, "行动号召")}
                  className="border-primary/20 bg-transparent hover:bg-primary/10"
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-foreground/90">{result.analysis.cta}</p>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="flex justify-center space-x-4">
        <Button
          onClick={handleDownload}
          variant="outline"
          className="border-primary/20 bg-transparent hover:bg-primary/10 px-6 py-3"
        >
          <Download className="h-4 w-4 mr-2" />
          下载结果
        </Button>
        <Button onClick={onReset} className="bg-primary hover:bg-primary/90 text-white px-6 py-3">
          <RefreshCw className="h-4 w-4 mr-2" />
          重新分析
        </Button>
      </div>
    </div>
  )
}
