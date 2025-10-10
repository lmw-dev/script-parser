"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Check } from "lucide-react"

export default function PricingPage() {
  return (
    <main className="container mx-auto py-16 lg:py-24 px-6 lg:px-12">
      {/* Header */}
      <div className="text-center mb-16">
        <h1 className="text-4xl lg:text-5xl font-bold text-foreground tracking-tight">
          价格方案
        </h1>
        <p className="mt-4 text-base lg:text-lg text-muted-foreground max-w-2xl mx-auto">
          选择最适合你的方案，即刻提升创作效率。
        </p>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        
        {/* Free Plan */}
        <div className="border-2 border-primary rounded-xl p-8 space-y-6 relative">
          {/* Badge */}
          <div className="absolute -top-3 left-1/2 -translate-x-1/2">
            <span className="px-3 py-1 bg-primary text-primary-foreground text-sm font-semibold rounded-full">
              默认开放
            </span>
          </div>
          
          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-foreground">免费版</h2>
            <div className="flex items-baseline space-x-2">
              <span className="text-4xl font-bold text-foreground">¥0</span>
              <span className="text-muted-foreground">/永久</span>
            </div>
            <p className="text-sm text-muted-foreground">
              适合所有创作者的基础工具
            </p>
          </div>
          
          <ul className="space-y-3">
            <li className="flex items-start">
              <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-foreground">高质量视频逐字稿</span>
            </li>
            <li className="flex items-start">
              <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-foreground">基础视频解析</span>
            </li>
          </ul>

          <Button 
            variant="outline" 
            className="w-full"
            asChild
          >
            <Link href="/">
              开始使用
            </Link>
          </Button>
        </div>

        {/* Pro Plan */}
        <div className="border border-border rounded-xl p-8 space-y-6 relative opacity-60">
          {/* Badge */}
          <div className="absolute -top-3 left-1/2 -translate-x-1/2">
            <span className="px-3 py-1 bg-muted text-muted-foreground text-sm font-semibold rounded-full">
              建设中
            </span>
          </div>

          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-foreground">专业版</h2>
            <div className="flex items-baseline space-x-2">
              <span className="text-4xl font-bold text-foreground">敬请期待</span>
            </div>
            <p className="text-sm text-muted-foreground">
              即将解锁强大的AI分析能力
            </p>
          </div>
          
          <ul className="space-y-3">
            <li className="flex items-start">
              <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-foreground">高质量视频逐字稿</span>
            </li>
            <li className="flex items-start">
              <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-foreground">基础视频解析</span>
            </li>
            <li className="flex items-start">
              <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-foreground">
                <span className="inline-flex items-center gap-2 px-2 py-1 bg-gradient-to-r from-orange-500/20 to-yellow-500/20 border border-orange-500/30 rounded-md font-semibold">
                  <span className="text-lg">✨</span>
                  AI结构化分析
                </span>
              </span>
            </li>
            <li className="flex items-start">
              <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-foreground">优先技术支持</span>
            </li>
          </ul>

          <Button 
            className="w-full" 
            disabled
          >
            即将推出
          </Button>
        </div>

      </div>

      {/* FAQ or Additional Info (Optional) */}
      <div className="mt-16 text-center">
        <p className="text-sm text-muted-foreground">
          有疑问? 随时 
          <a 
            href="mailto:contact@scriptparser.example.com" 
            className="text-primary hover:underline ml-1"
          >
            联系我们
          </a>
        </p>
      </div>
    </main>
  )
}

