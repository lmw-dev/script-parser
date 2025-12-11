/**
 * ResultSection component - displays analysis results with dynamic rendering
 * V3.0 - TOM-494: Supports both V2.0 (narrative) and V3.0 (tech spec) layouts
 */

"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Copy, Download, RefreshCw, CheckCircle, FileText, Lightbulb, Diamond, Goal, Quote, AlertCircle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { copyToClipboard, downloadAsMarkdown } from "@/lib/utils"
import type { V2NarrativeOutput, V3TechSpecOutput, DynamicAnalysisResult } from "@/types/script-parser.types"
import { ProductParametersCard } from "@/components/cards/ProductParametersCard"
import { SellingPointsCard } from "@/components/cards/SellingPointsCard"
import { PricingCard } from "@/components/cards/PricingCard"
import { ProsConsCard } from "@/components/cards/ProsConsCard"

export type ResultSectionProps = {
  readonly result: DynamicAnalysisResult
  readonly onReset: () => void
}

/**
 * Type guard: 检查是否为 V3.0 科技评测结果
 */
function isV3TechSpec(data: DynamicAnalysisResult): data is V3TechSpecOutput {
  return 'schema_type' in data && data.schema_type === 'v3_tech_spec'
}

/**
 * Type guard: 检查是否为 V2.0 通用叙事结果
 */
function isV2Narrative(data: DynamicAnalysisResult): data is V2NarrativeOutput {
  return 'analysis' in data && 'hook' in data.analysis
}

// KeyQuotesCard component for displaying key quotes (V2.0)
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

/**
 * V2.0 通用叙事布局
 */
function V2NarrativeLayout({ result, onReset, handleCopy, handleDownload }: {
  result: V2NarrativeOutput
  onReset: () => void
  handleCopy: (text: string, type: string) => void
  handleDownload: () => void
}) {
  return (
    <div className="w-full mx-auto space-y-4" data-testid="v2-narrative-layout">
      {/* Header - Compact */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-10 h-10 md:w-12 md:h-12 rounded-full bg-green-500/10 border-2 border-green-500/20">
          <CheckCircle className="h-5 w-5 md:h-6 md:w-6 text-green-500" />
        </div>
        <div>
          <h2 className="text-lg md:text-xl font-bold text-foreground">分析完成</h2>
          <p className="text-xs text-muted-foreground">AI已为您完成脚本结构化分析，结果如下。</p>
        </div>
      </div>

      {/* Main Content Grid - Web-Optimized */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {/* Left Column: Transcript */}
        <div className="lg:col-span-2">
          <Card className="h-full flex flex-col bg-card/80 backdrop-blur-sm border border-border shadow-lg transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3 flex-shrink-0">
              <CardTitle className="flex items-center text-base md:text-lg font-semibold">
                <FileText className="h-4 w-4 md:h-5 md:w-5 mr-2 text-primary" />
                完整逐字稿
              </CardTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleCopy(result.raw_transcript, "完整逐字稿")}
                className="text-muted-foreground hover:bg-primary/10 hover:text-primary h-8 w-8"
              >
                <Copy className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="flex-1 min-h-0 flex flex-col">
              <div className="prose prose-sm max-w-none flex-1 overflow-y-auto rounded-lg bg-input/50 p-3 border border-border text-sm">
                <p className="whitespace-pre-wrap leading-relaxed text-foreground/90">
                  {result.raw_transcript}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Actions and Analysis */}
        <div className="space-y-2">
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

/**
 * V3.0 科技评测空状态提示组件
 */
function TechSpecEmptyState() {
  return (
    <Card className="bg-amber-500/5 border border-amber-500/20 shadow-lg">
      <CardContent className="flex items-start gap-3 py-4 px-4">
        <AlertCircle className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="text-sm font-medium text-amber-700 dark:text-amber-400">
            未检测到科技评测内容
          </p>
          <p className="text-xs text-muted-foreground">
            此视频可能不是科技产品评测类型。建议使用「通用类型」重新分析，以获得更好的结果。
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

/**
 * V3.0 科技评测布局
 */
function V3TechSpecLayout({ result, onReset, handleCopy }: {
  result: V3TechSpecOutput
  onReset: () => void
  handleCopy: (text: string, type: string) => void
}) {
  // 检查是否有任何结构化数据
  const hasProductParameters = result.product_parameters && result.product_parameters.length > 0
  const hasSellingPoints = result.selling_points && result.selling_points.length > 0
  const hasPricingInfo = result.pricing_info && result.pricing_info.length > 0
  const hasEvaluation = result.subjective_evaluation && (
    (result.subjective_evaluation.pros && result.subjective_evaluation.pros.length > 0) ||
    (result.subjective_evaluation.cons && result.subjective_evaluation.cons.length > 0)
  )
  const hasAnyStructuredData = hasProductParameters || hasSellingPoints || hasPricingInfo || hasEvaluation

  const handleCopyAll = () => {
    // 生成 Markdown 格式的全部数据
    let markdown = "# 产品评测分析\n\n"

    // 产品参数
    markdown += "## 产品参数\n\n"
    result.product_parameters.forEach(param => {
      markdown += `- **${param.parameter}**: ${param.value}\n`
    })

    // 核心卖点
    markdown += "\n## 核心卖点\n\n"
    result.selling_points.forEach((point, index) => {
      markdown += `${index + 1}. ${point.point}\n`
      markdown += `   > ${point.context_snippet}\n\n`
    })

    // 价格信息
    markdown += "## 价格信息\n\n"
    result.pricing_info.forEach(pricing => {
      markdown += `- **${pricing.product}**: ${pricing.price}\n`
    })

    // 评测总结
    markdown += "\n## 评测总结\n\n"
    markdown += "### 优点\n\n"
    result.subjective_evaluation.pros.forEach(pro => {
      markdown += `- ${pro}\n`
    })
    markdown += "\n### 缺点\n\n"
    result.subjective_evaluation.cons.forEach(con => {
      markdown += `- ${con}\n`
    })

    handleCopy(markdown, "全部内容")
  }

  return (
    <div className="w-full mx-auto space-y-4" data-testid="v3-tech-spec-layout">
      {/* Header - Compact */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-10 h-10 md:w-12 md:h-12 rounded-full bg-green-500/10 border-2 border-green-500/20">
          <CheckCircle className="h-5 w-5 md:h-6 md:w-6 text-green-500" />
        </div>
        <div>
          <h2 className="text-lg md:text-xl font-bold text-foreground">科技评测分析完成</h2>
          <p className="text-xs text-muted-foreground">AI已为您提取产品技术规格和评测信息。</p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Column: Transcript */}
        <div className="lg:col-span-2">
          <Card className="h-full flex flex-col bg-card/80 backdrop-blur-sm border border-border shadow-lg transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3 flex-shrink-0">
              <CardTitle className="flex items-center text-base md:text-lg font-semibold">
                <FileText className="h-4 w-4 md:h-5 md:w-5 mr-2 text-primary" />
                完整逐字稿
              </CardTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleCopy(result.raw_transcript, "完整逐字稿")}
                className="text-muted-foreground hover:bg-primary/10 hover:text-primary h-8 w-8"
              >
                <Copy className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="flex-1 min-h-0 flex flex-col">
              <div className="prose prose-sm max-w-none flex-1 overflow-y-auto rounded-lg bg-input/50 p-3 border border-border text-sm">
                <p className="whitespace-pre-wrap leading-relaxed text-foreground/90">
                  {result.raw_transcript}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Actions and Analysis Cards */}
        <div className="space-y-2">
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
              {hasAnyStructuredData && (
              <Button
                onClick={handleCopyAll}
                variant="secondary"
                size="sm"
                className="w-full h-9 text-xs md:text-sm"
              >
                <Copy className="h-4 w-4 mr-2" />
                全部复制
              </Button>
              )}
            </CardContent>
          </Card>

          {/* Empty State or Analysis Cards */}
          {!hasAnyStructuredData ? (
            <TechSpecEmptyState />
          ) : (
            <>
          <ProductParametersCard parameters={result.product_parameters} onCopy={handleCopy} />
          <SellingPointsCard sellingPoints={result.selling_points} onCopy={handleCopy} />
          <PricingCard pricingInfo={result.pricing_info} onCopy={handleCopy} />
          <ProsConsCard evaluation={result.subjective_evaluation} onCopy={handleCopy} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}

/**
 * 主组件：动态路由到 V2.0 或 V3.0 布局
 */
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
      // V2.0 才有 download 功能
      if (isV2Narrative(result)) {
        downloadAsMarkdown(result)
        toast({
          title: "结果已开始下载",
          description: "文件将保存为 script-analysis.md",
          duration: 3000,
        })
      }
    } catch {
      toast({
        title: "下载失败",
        description: "无法生成下载文件，请稍后重试。",
        variant: "destructive",
      })
    }
  }

  // 动态渲染逻辑
  if (isV3TechSpec(result)) {
    return <V3TechSpecLayout result={result} onReset={onReset} handleCopy={handleCopy} />
  }

  if (isV2Narrative(result)) {
    return <V2NarrativeLayout result={result} onReset={onReset} handleCopy={handleCopy} handleDownload={handleDownload} />
  }

  // 错误状态：未知的结果类型
  return (
    <div className="w-full mx-auto space-y-4">
      <Card className="bg-destructive/10 border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">未知的分析结果格式</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            无法识别分析结果的类型。请刷新页面或重新提交。
          </p>
          <Button onClick={onReset} variant="outline" className="mt-4">
            <RefreshCw className="h-4 w-4 mr-2" />
            返回首页
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
