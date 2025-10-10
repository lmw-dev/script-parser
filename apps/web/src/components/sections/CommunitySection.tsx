import { Users, MessageCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function CommunitySection() {
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
              加入我们的创作"篝火"
            </h2>
            <p className="text-base lg:text-lg text-muted-foreground leading-relaxed">
              与数百位效率工具爱好者和独立开发者，共同交流心得、分享洞见，并第一时间体验新功能。
              一起参与产品迭代，让你的声音塑造工具的未来。
            </p>
          </div>

          {/* 行动号召 */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Button size="lg" className="min-w-[200px]">
              <MessageCircle className="w-5 h-5 mr-2" />
              加入微信社群
            </Button>
            <p className="text-sm text-muted-foreground">
              扫码备注"脚本快拆"
            </p>
          </div>

        </div>
      </div>
    </section>
  )
}

