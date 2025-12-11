import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // 启用 standalone 输出模式，用于 Docker 部署
  output: 'standalone',

  // 配置图片域名（使用 remotePatterns 替代已废弃的 domains）
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
  },

  // 环境变量配置
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || 
      (process.env.NODE_ENV === 'production' 
        ? 'https://sp.persimorrow.online/api'    // 使用 HTTPS，通过系统 Nginx 代理
        : 'http://localhost:8000'   // 本地开发环境
      ),
  },

  // 服务器外部包配置
  serverExternalPackages: [],

  // 配置 Server Actions 和 API Routes 的请求体大小限制
  experimental: {
    serverActions: {
      bodySizeLimit: '10mb', // 增加到10MB以支持视频文件上传
    },
  },

  // 禁用默认静态页面缓存头
  headers: async () => {
    return [
      {
        // 对所有 HTML 页面禁用缓存
        source: '/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
