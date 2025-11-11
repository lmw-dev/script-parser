/**
 * PricingCard - V3.0 价格信息卡片组件
 * @description 展示产品价格信息，突出显示价格
 */

"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Copy, DollarSign } from "lucide-react"

export type PricingInfo = {
  readonly product: string
  readonly price: string
  readonly context_snippet: string
}

export type PricingCardProps = {
  readonly pricingInfo: readonly PricingInfo[]
  readonly onCopy: (text: string, type: string) => void
}

/**
 * 价格信息卡片组件
 * @param pricingInfo - 价格信息数组
 * @param onCopy - 复制回调函数
 */
export function PricingCard({ pricingInfo, onCopy }: PricingCardProps) {
  if (!pricingInfo || pricingInfo.length === 0) {
    return null
  }

  return (
    <Card className="bg-card/80 backdrop-blur-sm border border-border shadow-lg">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pt-3 px-4">
        <CardTitle className="flex items-center text-xs md:text-sm font-semibold">
          <DollarSign className="h-4 w-4 mr-2 text-green-500" />
          价格信息
        </CardTitle>
      </CardHeader>
      <CardContent className="px-4 pb-3 space-y-3">
        {pricingInfo.map((pricing, index) => (
          <div 
            key={index}
            className="rounded-lg bg-muted/50 border border-border/50 p-3"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 space-y-1">
                <p className="text-xs md:text-sm font-medium text-foreground">
                  {pricing.product}
                </p>
                <p className="text-lg md:text-2xl font-bold text-green-600">
                  {pricing.price}
                </p>
                {pricing.context_snippet && (
                  <p className="text-xs text-muted-foreground italic mt-2">
                    引用: &ldquo;{pricing.context_snippet}&rdquo;
                  </p>
                )}
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onCopy(
                  `${pricing.product}: ${pricing.price}`,
                  `价格 ${pricing.product}`
                )}
                className="h-6 w-6 flex-shrink-0 text-muted-foreground hover:bg-primary/10 hover:text-primary"
              >
                <Copy className="h-3 w-3" />
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

