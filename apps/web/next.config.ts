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
};

export default nextConfig;
