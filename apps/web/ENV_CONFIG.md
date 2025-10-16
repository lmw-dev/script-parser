# 环境变量配置说明

## 概述

本项目使用环境变量来管理配置信息，包括 API 地址、社交媒体链接等。这样可以方便地修改配置，而无需修改代码。

## 配置文件

### `.env.example` (配置模板)
- 配置模板文件，**提交到 Git 仓库**
- 包含所有配置项和示例值
- 用于在不同环境快速创建配置

### `.env` (实际配置文件)
- 实际使用的配置文件，**不提交到 Git**
- 从 `.env.example` 复制创建
- 包含真实的配置值（如 API Key）

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
首次使用或在新环境部署时，复制模板文件：

```bash
cd apps/web
cp .env.example .env
```

### 2. 修改配置
编辑 `.env` 文件，填入您的实际配置：

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
2. **不要提交 .env**: `.env` 文件包含真实配置，不会被提交到 Git（已在 .gitignore 中）
3. **提交 .env.example**: `.env.example` 是模板，应该提交到 Git 供其他人参考
4. **重启服务器**: 修改环境变量后必须重启开发服务器
5. **默认值**: 所有配置都有默认值，即使不设置环境变量也能正常运行

## 生产环境部署

### 方案 1: 直接复制配置文件（推荐）
在服务器上：
```bash
cd apps/web
cp .env.example .env
# 然后编辑 .env 填入生产环境的实际配置
```

### 方案 2: 使用平台环境变量
在部署平台（如 Vercel、Netlify）的环境变量配置中设置：
1. 进入项目设置 → Environment Variables
2. 添加所需的环境变量
3. 重新部署项目

## 相关文件

- `apps/web/.env.example` - 配置模板（✅ 提交到 Git）
- `apps/web/.env` - 实际配置（❌ 不提交到 Git）
- `apps/web/src/lib/config.ts` - 配置管理文件

## 工作流程

1. **开发者 A** 创建 `.env.example` 并提交到 Git
2. **开发者 B** 拉取代码后执行 `cp .env.example .env`，然后填入自己的配置
3. **生产环境** 部署时执行 `cp .env.example .env`，然后填入生产配置
4. 每个人的 `.env` 都不会提交，互不影响
5. 更新配置项时，更新 `.env.example` 并提交，其他人同步更新自己的 `.env`

