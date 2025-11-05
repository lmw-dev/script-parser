'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Mail } from 'lucide-react'

type EmailSubscriptionFormProps = {
  title?: string
  description?: string
  onFormView?: () => void
  onFormInteraction?: () => void
}

export function EmailSubscriptionForm({
  title = '获取未来更新通知',
  description = '对更深入的 AI 洞察或专业版功能感兴趣？留下邮箱，第一时间获取更新通知和早鸟优惠！',
  onFormView,
  onFormInteraction,
}: EmailSubscriptionFormProps) {
  return (
    <Card 
      className="w-full max-w-2xl mx-auto border-none shadow-sm bg-card/50 backdrop-blur-sm"
      data-testid="email-subscription-form"
    >
      <CardHeader className="text-center space-y-2 pb-4">
        <div className="flex items-center justify-center gap-2">
          <Mail className="w-5 h-5 text-blue-500" />
          <CardTitle className="text-lg font-semibold">{title}</CardTitle>
        </div>
        <CardDescription className="text-xs text-muted-foreground">
          {description}
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <div 
          className="w-full"
          onClick={onFormInteraction}
          onFocus={onFormInteraction}
        >
          <iframe
            width="100%"
            height="300"
            src="https://4a87a233.sibforms.com/serve/MUIFAHkjxX-n9rrJ1j42WzYsEjUDdzVZ7rWbrmUKoKdpuTyA0NCSnQH213Ie7BQnp8s6K2R_mGOyzeSqdDeVvbqpZUnf6jwYau3gEsll3Ff793evyFySI2Tke5NultC_BWRg_4xKBOddAryu_udcDlfMXXLy02-doA0pzlrOtwgPwrh33_hXm1HQqCsjdlPKjq0FLFQu-PWj8tCy"
            frameBorder="0"
            scrolling="auto"
            allowFullScreen
            title="Email Subscription Form"
            style={{
              display: 'block',
              marginLeft: 'auto',
              marginRight: 'auto',
              maxWidth: '100%',
            }}
          />
        </div>
      </CardContent>
    </Card>
  )
}

