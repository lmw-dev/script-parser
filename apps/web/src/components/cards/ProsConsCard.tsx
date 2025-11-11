/**
 * ProsConsCard - V3.0 优缺点评价卡片组件
 * @description 两列布局展示产品优缺点
 */

"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Copy, Scale, ThumbsUp, ThumbsDown } from "lucide-react"

export type SubjectiveEvaluation = {
  readonly pros: readonly string[]
  readonly cons: readonly string[]
}

export type ProsConsCardProps = {
  readonly evaluation: SubjectiveEvaluation
  readonly onCopy: (text: string, type: string) => void
}

/**
 * 优缺点评价卡片组件
 * @param evaluation - 评价对象（优点+缺点）
 * @param onCopy - 复制回调函数
 */
export function ProsConsCard({ evaluation, onCopy }: ProsConsCardProps) {
  const hasPros = evaluation.pros && evaluation.pros.length > 0
  const hasCons = evaluation.cons && evaluation.cons.length > 0

  if (!hasPros && !hasCons) {
    return null
  }

  return (
    <Card className="bg-card/80 backdrop-blur-sm border border-border shadow-lg">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pt-3 px-4">
        <CardTitle className="flex items-center text-xs md:text-sm font-semibold">
          <Scale className="h-4 w-4 mr-2 text-purple-500" />
          评测总结
        </CardTitle>
      </CardHeader>
      <CardContent className="px-4 pb-3">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* 优点列 */}
          {hasPros && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-2">
                <ThumbsUp className="h-4 w-4 text-green-500" />
                <h4 className="text-xs md:text-sm font-semibold text-green-600">优点</h4>
              </div>
              <ul className="space-y-2">
                {evaluation.pros.map((pro, index) => (
                  <li 
                    key={index}
                    className="flex items-start justify-between gap-2 p-2 rounded-lg bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-900/50"
                  >
                    <span className="flex-1 text-xs leading-relaxed text-foreground/90">
                      • {pro}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onCopy(pro, `优点 ${index + 1}`)}
                      className="h-6 w-6 flex-shrink-0 text-muted-foreground hover:bg-green-100 hover:text-green-700 dark:hover:bg-green-900/30"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 缺点列 */}
          {hasCons && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-2">
                <ThumbsDown className="h-4 w-4 text-red-500" />
                <h4 className="text-xs md:text-sm font-semibold text-red-600">缺点</h4>
              </div>
              <ul className="space-y-2">
                {evaluation.cons.map((con, index) => (
                  <li 
                    key={index}
                    className="flex items-start justify-between gap-2 p-2 rounded-lg bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/50"
                  >
                    <span className="flex-1 text-xs leading-relaxed text-foreground/90">
                      • {con}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onCopy(con, `缺点 ${index + 1}`)}
                      className="h-6 w-6 flex-shrink-0 text-muted-foreground hover:bg-red-100 hover:text-red-700 dark:hover:bg-red-900/30"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

