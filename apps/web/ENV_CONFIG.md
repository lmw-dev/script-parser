# 环境变量配置说明

## 概述

本项目使用环境变量来管理配置信息，包括 API 地址、社交媒体链接等。这样可以方便地在不同环境（开发、生产）中使用不同的配置，而无需修改代码。

## 配置文件

### `.env.local` (本地开发环境)
用于本地开发，不会被提交到 Git 仓库。

### `.env.example` (配置模板)
配置模板文件，提交到 Git 仓库，供团队成员参考。

## 环境变量说明

### API 配置
- `NEXT_PUBLIC_API_URL`: 后端 API 地址
  - 开发环境: `http://localhost:8000`
  - 生产环境: 实际的 API 地址

### 社交媒体链接
- `NEXT_PUBLIC_GITHUB_URL`: GitHub 主页地址
- `NEXT_PUBLIC_TWITTER_URL`: Twitter 主页地址
- `NEXT_PUBLIC_BLOG_URL`: 博客地址
- `NEXT_PUBLIC_XIAOHONGSHU_URL`: 小红书主页地址

### 作者信息
- `NEXT_PUBLIC_AUTHOR_NAME`: 作者名称
- `NEXT_PUBLIC_AUTHOR_TITLE`: 作者职位描述

## 快速开始

### 1. 复制模板文件
```bash
cp .env.example .env.local
```

### 2. 修改配置
编辑 `.env.local` 文件，填入您的实际配置：

```bash
# Social Media Links
NEXT_PUBLIC_GITHUB_URL=https://github.com/your-username
NEXT_PUBLIC_TWITTER_URL=https://twitter.com/your-username
NEXT_PUBLIC_BLOG_URL=https://blog.example.com
NEXT_PUBLIC_XIAOHONGSHU_URL=https://xiaohongshu.com/user/profile/your-id

# Author Information
NEXT_PUBLIC_AUTHOR_NAME=Your Name
NEXT_PUBLIC_AUTHOR_TITLE=你的职位描述
```

### 3. 重启开发服务器
修改环境变量后需要重启开发服务器才能生效：

```bash
pnpm dev
```

## 在代码中使用

所有环境变量都通过 `src/lib/config.ts` 统一管理和导出：

```typescript
import { config } from '@/lib/config'

// 使用配置
const githubUrl = config.social.github
const authorName = config.author.name
```

## 注意事项

1. **环境变量前缀**: Next.js 中，只有以 `NEXT_PUBLIC_` 开头的环境变量才能在浏览器端访问
2. **不要提交敏感信息**: `.env.local` 文件已添加到 `.gitignore`，不会被提交到 Git
3. **重启服务器**: 修改环境变量后必须重启开发服务器
4. **默认值**: 所有配置都有默认值，即使不设置环境变量也能正常运行

## 生产环境部署

在生产环境中，需要在部署平台（如 Vercel、Netlify）的环境变量配置中设置这些变量。

### Vercel 配置示例
1. 进入项目设置 → Environment Variables
2. 添加所需的环境变量
3. 重新部署项目

## 相关文件

- `apps/web/.env.local` - 本地开发配置（不提交）
- `apps/web/.env.example` - 配置模板（提交到 Git）
- `apps/web/src/lib/config.ts` - 配置管理文件

