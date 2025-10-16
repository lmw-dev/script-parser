/**
 * Application configuration from environment variables
 * All public environment variables must be prefixed with NEXT_PUBLIC_
 */

export const config = {
  api: {
    url: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  social: {
    github: process.env.NEXT_PUBLIC_GITHUB_URL || 'https://github.com/lmw-dev',
    twitter: process.env.NEXT_PUBLIC_TWITTER_URL || 'https://twitter.com/lmw_dev',
    blog: process.env.NEXT_PUBLIC_BLOG_URL || 'https://blog.lmw.dev',
    xiaohongshu: process.env.NEXT_PUBLIC_XIAOHONGSHU_URL || 'https://xiaohongshu.com/user/profile/xxx',
  },
  author: {
    name: process.env.NEXT_PUBLIC_AUTHOR_NAME || '刘明伟',
    title: process.env.NEXT_PUBLIC_AUTHOR_TITLE || '独立开发者 · 效率工具探索者',
  },
} as const

