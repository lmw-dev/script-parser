import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Analytics } from "@vercel/analytics/next"
import { Toaster } from "@/components/ui/toaster"

import { Header } from "@/components/layout/Header"
import { Footer } from "@/components/layout/Footer"
import "./globals.css"

export const metadata: Metadata = {
  metadataBase: new URL('https://sp.persimorrow.online'),
  title: {
    template: '%s | AI 脚本快拆',
    default: 'AI 脚本快拆 - 智能视频脚本分析工具',
  },
  description: '粘贴视频链接,即刻获取AI结构化分析脚本,让你的内容创作效率倍增。为效率驱动的创作者打造小而美的AI工具。',
  keywords: ['AI脚本分析', '视频脚本', '内容创作', '效率工具', '视频解析', 'AI工具'],
  authors: [{ name: '刘明伟', url: 'https://blog.lmw.dev' }],
  creator: '刘明伟',
  generator: "v0.app",
  openGraph: {
    type: 'website',
    locale: 'zh_CN',
    url: 'https://sp.persimorrow.online',
    siteName: 'AI 脚本快拆',
    title: 'AI 脚本快拆 - 智能视频脚本分析工具',
    description: '粘贴视频链接,即刻获取AI结构化分析脚本,让你的内容创作效率倍增。',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'AI 脚本快拆',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI 脚本快拆 - 智能视频脚本分析工具',
    description: '粘贴视频链接,即刻获取AI结构化分析脚本,让你的内容创作效率倍增。',
    images: ['/og-image.png'],
    creator: '@lmw_dev',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-CN">
      <body className={`font-sans ${GeistSans.variable} ${GeistMono.variable}`}>
        <div className="min-h-screen flex flex-col bg-background">
          <Header />
          <main className="flex-grow flex flex-col">
            {children}
          </main>
          <Footer />
        </div>
        <Toaster />
        <Analytics />
      </body>
    </html>
  )
}
