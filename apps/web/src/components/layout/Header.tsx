'use client'

import Link from 'next/link'
import { Sparkles, Github } from 'lucide-react'
import { config } from '@/lib/config'

export function Header() {
  return (
    <header className="w-full bg-background/80 backdrop-blur-sm border-b border-border sticky top-0 z-50">
      <div className="container mx-auto flex h-16 items-center justify-between px-6 lg:px-12">
        
        {/* Left Side: Brand */}
        <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <span className="font-bold text-lg text-foreground">AI 脚本快拆</span>
        </Link>

        {/* Right Side: Navigation */}
        <nav className="flex items-center space-x-6">
          <Link 
            href="/" 
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            首页
          </Link>
          <Link 
            href="/pricing" 
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            价格
          </Link>
          <Link 
            href={config.social.blog} 
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            博客
          </Link>
          <a 
            href={config.social.github} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="text-muted-foreground hover:text-foreground transition-colors"
            aria-label="GitHub"
          >
            <Github className="w-5 h-5" />
          </a>
        </nav>
      </div>
    </header>
  )
}
