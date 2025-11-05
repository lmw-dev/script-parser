'use client'

import Image from 'next/image'
import { Coffee } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

type QrProvider = 'wechat' | 'alipay'

type DonationSectionProps = {
  wechatQrPath: string
  alipayQrPath: string
  onQrClick?: (provider: QrProvider) => void
  onQrView?: (provider: QrProvider) => void
}

export function DonationSection({
  wechatQrPath,
  alipayQrPath,
  onQrClick,
  onQrView,
}: DonationSectionProps) {
  const handleQrClick = (provider: QrProvider) => {
    if (onQrClick) {
      onQrClick(provider)
    }
  }

  const handleQrView = (provider: QrProvider) => {
    if (onQrView) {
      onQrView(provider)
    }
  }

  return (
    <Card 
      className="w-full max-w-2xl mx-auto border-none shadow-sm bg-card/50 backdrop-blur-sm" 
      data-testid="donation-section"
    >
      <CardHeader className="text-center space-y-2 pb-4">
        <div className="flex items-center justify-center gap-2">
          <Coffee className="w-5 h-5 text-amber-500" />
          <CardTitle className="text-lg font-semibold">支持开发者</CardTitle>
        </div>
        <CardDescription className="text-xs text-muted-foreground">
          如果这个工具对你有帮助，可以请我喝杯咖啡～（完全自愿，无任何强制）
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* WeChat QR Code */}
          <div
            className="flex flex-col items-center space-y-3 p-4 rounded-lg border border-border hover:border-primary/50 transition-colors cursor-pointer"
            data-testid="donation-wechat-qr"
            onClick={() => handleQrClick('wechat')}
            onMouseEnter={() => handleQrView('wechat')}
          >
            <h3 className="text-sm font-medium text-foreground">微信支付</h3>
            <div className="relative w-40 h-40 bg-white p-2 rounded-md">
              <Image
                src={wechatQrPath}
                alt="微信支付二维码"
                fill
                className="object-contain"
                priority
              />
            </div>
            <p className="text-xs text-muted-foreground">微信扫码支持</p>
          </div>

          {/* Alipay QR Code */}
          <div
            className="flex flex-col items-center space-y-3 p-4 rounded-lg border border-border hover:border-primary/50 transition-colors cursor-pointer"
            data-testid="donation-alipay-qr"
            onClick={() => handleQrClick('alipay')}
            onMouseEnter={() => handleQrView('alipay')}
          >
            <h3 className="text-sm font-medium text-foreground">支付宝</h3>
            <div className="relative w-40 h-40 bg-white p-2 rounded-md">
              <Image
                src={alipayQrPath}
                alt="支付宝二维码"
                fill
                className="object-contain"
                priority
              />
            </div>
            <p className="text-xs text-muted-foreground">支付宝扫码支持</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

