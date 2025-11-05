/**
 * ResultSection component - displays analysis results
 * Based on TOM-318, TOM-346 and TOM-347 specifications
 */

"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Copy, Download, RefreshCw, CheckCircle, FileText, Lightbulb, Diamond, Goal, Quote } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { copyToClipboard, downloadAsMarkdown } from "@/lib/utils"
import type { AnalysisResult } from "@/types/script-parser.types"

// Update props to remove onCopy and onDownload as they are now handled internally
export type ResultSectionProps = {
  readonly result: AnalysisResult
  readonly onReset: () => void
}

// KeyQuotesCard component for displaying key quotes
function KeyQuotesCard({ quotes, onCopy }: { quotes: readonly string[]; onCopy: (text: string, type: string) => void }) {
  return (
    <Card className="bg-card/80 backdrop-blur-sm border border-border shadow-lg">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pt-3 px-4">
        <CardTitle className="flex items-center text-xs md:text-sm font-semibold">
          <Quote className="h-4 w-4 mr-2 text-purple-500" />
          金句
        </CardTitle>
      </CardHeader>
      <CardContent className="px-4 pb-3 space-y-2">
        {quotes.map((quote, index) => (
          <div key={index} className="flex items-start justify-between gap-2 p-2 rounded-lg bg-muted/50 border border-border/50">
            <blockquote className="flex-1 text-xs leading-relaxed text-foreground/90 italic line-clamp-2">
              &ldquo;{quote}&rdquo;
            </blockquote>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onCopy(quote, `金句 ${index + 1}`)}
              className="flex-shrink-0 text-muted-foreground hover:bg-primary/10 hover:text-primary h-6 w-6"
            >
              <Copy className="h-3 w-3" />
            </Button>
          </div>
        ))}
      </CardContent>
    </Card>
  )
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
    } catch {
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
    } catch {
      toast({
        title: "下载失败",
        description: "无法生成下载文件，请稍后重试。",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="w-full mx-auto space-y-3 md:space-y-4">
      {/* Header - Compact */}
      <div className="text-center space-y-1">
        <div className="inline-flex items-center justify-center w-12 h-12 md:w-14 md:h-14 rounded-full bg-green-500/10 border-2 border-green-500/20">
          <CheckCircle className="h-6 w-6 md:h-7 md:w-7 text-green-500" />
        </div>
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-foreground">分析完成</h2>
          <p className="text-xs md:text-sm text-muted-foreground">AI已为您完成脚本结构化分析，结果如下。</p>
        </div>
      </div>

      {/* Main Content Grid - Web-Optimized */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 md:gap-5 lg:gap-6">
        
        {/* Left Column: Transcript */}
        <div className="lg:col-span-2">
          <Card className="h-full bg-card/80 backdrop-blur-sm border border-border shadow-lg transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="flex items-center text-base md:text-lg font-semibold">
                <FileText className="h-4 w-4 md:h-5 md:w-5 mr-2 text-primary" />
                完整逐字稿
              </CardTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleCopy(result.cleaned_transcript, "完整逐字稿")}
                className="text-muted-foreground hover:bg-primary/10 hover:text-primary h-8 w-8"
              >
                <Copy className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm max-w-none h-[350px] lg:h-[450px] overflow-y-auto rounded-lg bg-input/50 p-3 border border-border text-sm">
                <p className="whitespace-pre-wrap leading-relaxed text-foreground/90">
                  {result.cleaned_transcript}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Actions and Analysis */}
        <div className="space-y-2 md:space-y-3">
          {/* Action Panel */}
          <Card className="bg-card/80 backdrop-blur-sm border border-border shadow-lg">
            <CardHeader className="pb-2 pt-3 px-4">
              <CardTitle className="text-sm md:text-base font-semibold">操作</CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3 flex flex-col space-y-2">
              <Button onClick={onReset} size="sm" className="w-full h-9 text-xs md:text-sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                再分析一个
              </Button>
              <Button
                onClick={handleDownload}
                variant="secondary"
                size="sm"
                className="w-full h-9 text-xs md:text-sm"
              >
                <Download className="h-4 w-4 mr-2" />
                下载 Markdown
              </Button>
            </CardContent>
          </Card>

          {/* Analysis Cards - Compact with minimal padding */}
          <Card className="bg-card/80 backdrop-blur-sm border border-border shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pt-3 px-4">
              <CardTitle className="flex items-center text-xs md:text-sm font-semibold">
                <Lightbulb className="h-4 w-4 mr-2 text-yellow-500" />
                钩子
              </CardTitle>
              <Button variant="ghost" size="icon" onClick={() => handleCopy(result.analysis.hook, "钩子")} className="h-6 w-6 -mr-1">
                <Copy className="h-3 w-3" />
              </Button>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <p className="text-xs leading-relaxed text-muted-foreground line-clamp-3">{result.analysis.hook}</p>
            </CardContent>
          </Card>

          <Card className="bg-card/80 backdrop-blur-sm border border-border shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pt-3 px-4">
              <CardTitle className="flex items-center text-xs md:text-sm font-semibold">
                <Diamond className="h-4 w-4 mr-2 text-cyan-500" />
                核心
              </CardTitle>
              <Button variant="ghost" size="icon" onClick={() => handleCopy(result.analysis.core, "核心")} className="h-6 w-6 -mr-1">
                <Copy className="h-3 w-3" />
              </Button>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <p className="text-xs leading-relaxed text-muted-foreground line-clamp-3">{result.analysis.core}</p>
            </CardContent>
          </Card>

          <Card className="bg-card/80 backdrop-blur-sm border border-border shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pt-3 px-4">
              <CardTitle className="flex items-center text-xs md:text-sm font-semibold">
                <Goal className="h-4 w-4 mr-2 text-green-500" />
                行动号召
              </CardTitle>
              <Button variant="ghost" size="icon" onClick={() => handleCopy(result.analysis.cta, "行动号召")} className="h-6 w-6 -mr-1">
                <Copy className="h-3 w-3" />
              </Button>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <p className="text-xs leading-relaxed text-muted-foreground line-clamp-3">{result.analysis.cta}</p>
            </CardContent>
          </Card>

          {/* V3.0: KeyQuotesCard - Conditionally render if key_quotes exists and has items */}
          {result.analysis.key_quotes && result.analysis.key_quotes.length > 0 && (
            <KeyQuotesCard quotes={result.analysis.key_quotes} onCopy={handleCopy} />
          )}
        </div>
      </div>
    </div>
  )
}
