/**
 * SellingPointsCard - V3.0 核心卖点卡片组件
 * @description 展示产品卖点，支持展开/折叠原文引用
 */

"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Copy, Sparkles, ChevronDown } from "lucide-react"
import { useState } from "react"

export type SellingPoint = {
  readonly point: string
  readonly context_snippet: string
}

export type SellingPointsCardProps = {
  readonly sellingPoints: readonly SellingPoint[]
  readonly onCopy: (text: string, type: string) => void
}

/**
 * 核心卖点卡片组件
 * @param sellingPoints - 卖点数组
 * @param onCopy - 复制回调函数
 */
export function SellingPointsCard({ sellingPoints, onCopy }: SellingPointsCardProps) {
  const [openItems, setOpenItems] = useState<Set<number>>(new Set())

  if (!sellingPoints || sellingPoints.length === 0) {
    return null
  }

  const toggleItem = (index: number) => {
    setOpenItems((prev) => {
      const next = new Set(prev)
      if (next.has(index)) {
        next.delete(index)
      } else {
        next.add(index)
      }
      return next
    })
  }

  return (
    <Card className="bg-card/80 backdrop-blur-sm border border-border shadow-lg">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pt-3 px-4">
        <CardTitle className="flex items-center text-xs md:text-sm font-semibold">
          <Sparkles className="h-4 w-4 mr-2 text-yellow-500" />
          核心卖点
        </CardTitle>
      </CardHeader>
      <CardContent className="px-4 pb-3 space-y-2">
        {sellingPoints.map((sellingPoint, index) => (
          <Collapsible
            key={index}
            open={openItems.has(index)}
            onOpenChange={() => toggleItem(index)}
          >
            <div className="rounded-lg bg-muted/50 border border-border/50 p-3">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs md:text-sm font-medium text-foreground">
                      • {sellingPoint.point}
                    </span>
                  </div>
                  <CollapsibleContent>
                    <div className="mt-2 pt-2 border-t border-border/50">
                      <p className="text-xs text-muted-foreground italic">
                        原文: &ldquo;{sellingPoint.context_snippet}&rdquo;
                      </p>
                    </div>
                  </CollapsibleContent>
                </div>
                <div className="flex items-center gap-1">
                  <CollapsibleTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6 text-muted-foreground hover:bg-primary/10 hover:text-primary"
                    >
                      <ChevronDown 
                        className={`h-3 w-3 transition-transform ${
                          openItems.has(index) ? "transform rotate-180" : ""
                        }`} 
                      />
                    </Button>
                  </CollapsibleTrigger>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => onCopy(sellingPoint.point, `卖点 ${index + 1}`)}
                    className="h-6 w-6 text-muted-foreground hover:bg-primary/10 hover:text-primary"
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>
          </Collapsible>
        ))}
      </CardContent>
    </Card>
  )
}

