import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // 启用 standalone 输出模式，用于 Docker 部署
  output: 'standalone',

  // 配置图片域名
  images: {
    domains: ['localhost'],
  },

  // 环境变量配置
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // 服务器外部包配置
  serverExternalPackages: [],

  // 配置 Server Actions 和 API Routes 的请求体大小限制
  experimental: {
    serverActions: {
      bodySizeLimit: '10mb', // 增加到10MB以支持视频文件上传
    },
  },

  // 注意：Next.js 15的API Routes配置已移至route.ts文件中处理
};

export default nextConfig;
