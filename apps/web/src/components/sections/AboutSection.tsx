import Image from 'next/image'
import { Github, Twitter, BookOpen, Instagram } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function AboutSection() {
  return (
    <section className="w-full bg-muted/30 border-t border-border py-12 lg:py-20">
      <div className="container mx-auto px-6 lg:px-12">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8 lg:gap-12 items-center">
          
          {/* 左侧：头像 */}
          <div className="md:col-span-2 flex justify-center md:justify-end">
            <div className="relative">
              <Image
                src="/placeholder-user.png"
                alt="刘明伟的头像"
                width={200}
                height={200}
                className="rounded-full shadow-lg border-4 border-white dark:border-gray-800"
                priority
              />
            </div>
          </div>

          {/* 右侧：文字与链接 */}
          <div className="md:col-span-3 space-y-6 text-center md:text-left">
            <div className="space-y-2">
              <h2 className="text-3xl lg:text-4xl font-bold text-foreground">
                关于创作者
              </h2>
              <p className="text-muted-foreground">独立开发者 · 效率工具探索者</p>
            </div>
            
            <div className="space-y-4 text-base lg:text-lg text-foreground/80 leading-relaxed">
              <p>
                嗨，我是刘明伟（LMW）👋 一名独立开发者和效率工具的探索者。
              </p>
              <p>
                我相信「工匠精神 + 商业思维」的结合。通过AI技术，我希望打造真正能提升创作者效率的工具，
                让技术为内容创作者赋能。
              </p>
              <p>
                「脚本快拆」是我的第一个AI产品实验，期待与你一起见证它的成长 🚀
              </p>
            </div>
            
            {/* 社交媒体链接 */}
            <div className="flex flex-wrap justify-center md:justify-start gap-3 pt-4">
              <Button variant="outline" size="sm" asChild>
                <a href="https://github.com/lmw-dev" target="_blank" rel="noopener noreferrer">
                  <Github className="w-4 h-4 mr-2" />
                  GitHub
                </a>
              </Button>
              <Button variant="outline" size="sm" asChild>
                <a href="https://twitter.com/lmw_dev" target="_blank" rel="noopener noreferrer">
                  <Twitter className="w-4 h-4 mr-2" />
                  Twitter
                </a>
              </Button>
              <Button variant="outline" size="sm" asChild>
                <a href="https://blog.lmw.dev" target="_blank" rel="noopener noreferrer">
                  <BookOpen className="w-4 h-4 mr-2" />
                  博客
                </a>
              </Button>
              <Button variant="outline" size="sm" asChild>
                <a href="https://xiaohongshu.com/user/profile/xxx" target="_blank" rel="noopener noreferrer">
                  <Instagram className="w-4 h-4 mr-2" />
                  小红书
                </a>
              </Button>
            </div>
          </div>

        </div>
      </div>
    </section>
  )
}

