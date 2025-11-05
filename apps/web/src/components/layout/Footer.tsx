import Link from 'next/link'
import { Github, Twitter, BookOpen, Instagram } from 'lucide-react'

export function Footer() {
  const currentYear = new Date().getFullYear()
  
  const socialLinks = [
    { name: 'GitHub', icon: Github, href: 'https://github.com/lmw-dev' },
    { name: 'Twitter', icon: Twitter, href: 'https://twitter.com/lmw_dev' },
    { name: '博客', icon: BookOpen, href: 'https://blog.lmw.dev' },
    { name: '小红书', icon: Instagram, href: 'https://xiaohongshu.com/user/profile/xxx' },
  ]

  return (
    <footer className="w-full bg-muted/20 border-t border-border mt-12">
      <div className="container mx-auto py-8 px-6 lg:px-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
          
          {/* Column 1: Brand */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground">AI 脚本快拆</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              为效率驱动的创作者，打造小而美的AI工具。
            </p>
          </div>

          {/* Column 2: Navigation */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground">导航</h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/" 
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  首页
                </Link>
              </li>
              <li>
                <Link 
                  href="/pricing" 
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  价格
                </Link>
              </li>
              <li>
                <Link 
                  href="https://blog.lmw.dev" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  博客
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 3: Social Matrix */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground">关注我</h3>
            <div className="flex flex-wrap gap-3">
              {socialLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                  aria-label={link.name}
                >
                  <link.icon className="w-4 h-4" />
                  <span>{link.name}</span>
                </a>
              ))}
            </div>
          </div>

        </div>

        {/* Copyright */}
        <div className="mt-8 border-t border-border pt-6 text-center">
          <p className="text-xs text-muted-foreground">
            &copy; {currentYear} AI 脚本快拆. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}

