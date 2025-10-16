'use client'

import { useState } from 'react'
import { Users, MessageCircle } from 'lucide-react'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

export function CommunitySection() {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  return (
    <section className="w-full bg-primary/5 border-y border-border py-16 lg:py-24">
      <div className="container mx-auto px-6 lg:px-12">
        <div className="max-w-2xl mx-auto text-center space-y-8">
          
          {/* 视觉图标 */}
          <div className="flex justify-center">
            <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center">
              <Users className="w-8 h-8 text-primary" />
            </div>
          </div>

          {/* 标题与价值主张 */}
          <div className="space-y-4">
            <h2 className="text-3xl lg:text-4xl font-bold text-foreground tracking-tight">
              加入我们的创作&ldquo;篝火&rdquo;
            </h2>
            <p className="text-base lg:text-lg text-muted-foreground leading-relaxed">
              与数百位效率工具爱好者和独立开发者，共同交流心得、分享洞见，并第一时间体验新功能。
              一起参与产品迭代，让你的声音塑造工具的未来。
            </p>
          </div>

          {/* 行动号召 */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Button 
              size="lg" 
              className="min-w-[200px]"
              onClick={() => setIsDialogOpen(true)}
            >
              <MessageCircle className="w-5 h-5 mr-2" />
              加入微信社群
            </Button>
            <p className="text-sm text-muted-foreground">
              扫码备注&ldquo;脚本快拆&rdquo;
            </p>
          </div>

        </div>
      </div>

      {/* 微信群二维码对话框 */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-center text-2xl">加入微信社群</DialogTitle>
            <DialogDescription className="text-center">
              扫描下方二维码，备注「脚本快拆」加入我们
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col items-center space-y-4 py-4">
            <div className="relative w-64 h-64 bg-muted rounded-lg overflow-hidden border-2 border-border">
              <Image
                src="/wechat-qrcode.png"
                alt="微信群二维码"
                fill
                className="object-contain p-2"
                priority
              />
            </div>
            <div className="text-center space-y-2">
              <p className="text-sm text-muted-foreground">
                💡 扫码后请备注「脚本快拆」
              </p>
              <p className="text-xs text-muted-foreground">
                如二维码过期，请联系管理员
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </section>
  )
}

