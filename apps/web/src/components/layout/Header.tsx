'use client'

import Link from 'next/link'
import { Sparkles, Wand2, DollarSign, Github } from 'lucide-react'

export function Header() {
  return (
    <header className="h-14 bg-primary border-b border-primary/20 flex items-center justify-between px-6 flex-shrink-0">
      <Link href="/" className="flex items-center space-x-3">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 bg-white/20 rounded flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="text-white font-semibold text-sm">AI 脚本快拆</span>
          <span className="text-white/60 text-xs">by v0</span>
        </div>
      </Link>
      <div className="flex items-center space-x-2">
        <button className="px-3 py-1.5 text-white/80 hover:text-white text-xs font-medium rounded-md transition-colors flex items-center space-x-2">
          <Wand2 className="w-4 h-4" />
          <span>工作原理</span>
        </button>
        <button className="px-3 py-1.5 text-white/80 hover:text-white text-xs font-medium rounded-md transition-colors flex items-center space-x-2">
          <DollarSign className="w-4 h-4" />
          <span>价格</span>
        </button>
        <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="px-3 py-1.5 text-white/80 hover:text-white text-xs font-medium rounded-md transition-colors flex items-center space-x-2">
          <Github className="w-4 h-4" />
          <span>GitHub</span>
        </a>
      </div>
    </header>
  )
}
