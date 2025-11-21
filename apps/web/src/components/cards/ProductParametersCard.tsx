/**
 * ProductParametersCard - V3.0 产品参数卡片组件
 * @description 以表格形式显示产品技术参数，支持单行复制
 */

"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Copy, Cpu } from "lucide-react"

export type ProductParameter = {
  readonly parameter: string
  readonly value: string
}

export type ProductParametersCardProps = {
  readonly parameters: readonly ProductParameter[]
  readonly onCopy: (text: string, type: string) => void
}

/**
 * 产品参数卡片组件
 * @param parameters - 产品参数数组
 * @param onCopy - 复制回调函数
 */
export function ProductParametersCard({ parameters, onCopy }: ProductParametersCardProps) {
  // Filter out "价格" (Price) parameters as they are better displayed in the PricingCard
  const filteredParameters = parameters?.filter(p => p.parameter !== "价格") || []

  if (filteredParameters.length === 0) {
    return null
  }

  return (
    <Card className="bg-card/80 backdrop-blur-sm border border-border shadow-lg">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pt-3 px-4">
        <CardTitle className="flex items-center text-xs md:text-sm font-semibold">
          <Cpu className="h-4 w-4 mr-2 text-blue-500" />
          产品参数
        </CardTitle>
      </CardHeader>
      <CardContent className="px-4 pb-3">
        <div className="rounded-lg border border-border overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                <TableHead className="h-10 text-xs font-medium">参数</TableHead>
                <TableHead className="h-10 text-xs font-medium">值</TableHead>
                <TableHead className="h-10 w-16 text-xs font-medium text-center">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredParameters.map((param, index) => (
                <TableRow
                  key={index}
                  className="hover:bg-muted/50 transition-colors"
                >
                  <TableCell className="py-3 text-xs font-medium">{param.parameter}</TableCell>
                  <TableCell className="py-3 text-xs">{param.value}</TableCell>
                  <TableCell className="py-3 text-center">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onCopy(`${param.parameter}: ${param.value}`, `参数 ${param.parameter}`)}
                      className="h-6 w-6 text-muted-foreground hover:bg-primary/10 hover:text-primary"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}

