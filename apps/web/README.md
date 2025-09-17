# 🎬 AI脚本快拆 - Web Frontend

> 智能视频脚本分析工具的现代化Web前端应用

[![Next.js](https://img.shields.io/badge/Next.js-15.5.3-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-v4-38bdf8)](https://tailwindcss.com/)
[![shadcn/ui](https://img.shields.io/badge/shadcn%2Fui-latest-000000)](https://ui.shadcn.com/)

## 📖 项目简介

AI脚本快拆是一个专业级的视频脚本分析工具，支持从抖音、小红书等主流平台提取视频链接，自动生成逐字稿并进行AI结构化分析。

### ✨ 核心功能

- 🔗 **智能URL提取** - 从分享文本中自动识别并提取视频链接
- 📁 **文件上传支持** - 支持本地视频文件上传分析
- 🤖 **AI结构化分析** - 自动提取Hook、Core、CTA三段式脚本结构
- 📝 **逐字稿生成** - 高质量ASR服务提取完整逐字稿
- 💾 **结果导出** - 支持Markdown格式结果下载
- 🎨 **现代化UI** - 基于Rondo设计系统的精美界面

## 🛠️ 技术栈

### 核心框架
- **[Next.js 15](https://nextjs.org/)** - React全栈框架 (App Router)
- **[TypeScript 5](https://www.typescriptlang.org/)** - 类型安全的JavaScript
- **[React 19](https://react.dev/)** - 用户界面库

### 样式与UI
- **[Tailwind CSS v4](https://tailwindcss.com/)** - 原子化CSS框架
- **[shadcn/ui](https://ui.shadcn.com/)** - 高质量React组件库
- **[Radix UI](https://www.radix-ui.com/)** - 无障碍UI基础组件
- **[Lucide React](https://lucide.dev/)** - 美观的图标库
- **[Geist Font](https://vercel.com/font)** - Vercel现代字体

### 开发工具
- **[ESLint](https://eslint.org/)** - 代码质量检查
- **[Prettier](https://prettier.io/)** - 代码格式化
- **[Husky](https://typicode.github.io/husky/)** - Git钩子管理
- **[Commitlint](https://commitlint.js.org/)** - 提交信息规范

## 🚀 快速开始

### 环境要求

- Node.js >= 20.0.0
- pnpm >= 8.0.0

### 安装依赖

```bash
# 从项目根目录运行
pnpm install

# 或者只安装web应用依赖
pnpm --filter web install
```

### 开发服务器

```bash
# 启动开发服务器
pnpm --filter web dev

# 或者从项目根目录
pnpm dev:web
```

打开 [http://localhost:3000](http://localhost:3000) 查看应用。

### 构建生产版本

```bash
# 构建生产版本
pnpm --filter web build

# 启动生产服务器
pnpm --filter web start
```

## 🧪 测试

### 单元测试

项目使用Jest + Testing Library进行单元测试。

```bash
# 运行所有测试
pnpm --filter web test

# 监听模式运行测试
pnpm --filter web test:watch

# 生成测试覆盖率报告
pnpm --filter web test:coverage
```

### 测试文件结构

```
src/
├── lib/
│   ├── validation.ts
│   └── __tests__/
│       └── validation.test.ts    # 验证工具单元测试
├── components/
│   └── __tests__/
│       └── *.test.tsx            # 组件测试
└── __tests__/
    └── *.test.ts                 # 其他测试文件
```

### 测试覆盖范围

- ✅ **URL验证与提取** - 测试抖音/小红书分享文本URL提取
- ✅ **文件验证** - 测试视频文件类型和大小验证
- ✅ **组件交互** - 测试受控组件状态管理
- ✅ **错误处理** - 测试各种边界情况和错误场景

## 📝 代码规范

### 提交信息规范

项目使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```bash
# 功能开发
feat(web): add new component

# 问题修复  
fix(web): resolve validation issue

# 重构代码
refactor(web): improve component structure

# 文档更新
docs(web): update README

# 样式调整
style(web): fix formatting

# 测试相关
test(web): add unit tests
```

### 代码格式化

```bash
# 检查代码格式
pnpm --filter web format:check

# 自动格式化代码
pnpm --filter web format

# 运行ESLint检查
pnpm --filter web lint
```

## 📁 项目结构

```
apps/web/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── globals.css          # 全局样式
│   │   ├── layout.tsx           # 根布局
│   │   └── page.tsx             # 主页面
│   ├── components/
│   │   ├── sections/            # 业务组件
│   │   │   ├── InputSection.tsx    # 输入组件 (受控)
│   │   │   ├── ProcessingSection.tsx # 处理状态
│   │   │   ├── ResultSection.tsx    # 结果展示
│   │   │   └── ErrorSection.tsx     # 错误处理
│   │   └── ui/                  # shadcn/ui组件库
│   ├── lib/
│   │   ├── api-client.ts        # API客户端
│   │   ├── validation.ts        # 验证工具 (增强)
│   │   └── utils.ts             # 工具函数
│   ├── hooks/
│   │   └── use-toast.ts         # Toast钩子
│   ├── types/
│   │   └── script-parser.types.ts # 类型定义
│   └── docs/                    # 技术文档
├── public/                      # 静态资源
├── package.json                 # 依赖配置
├── next.config.ts              # Next.js配置
├── tailwind.config.ts          # Tailwind配置
└── tsconfig.json               # TypeScript配置
```

## 🏗️ 架构设计

### 状态管理模式

- **受控组件** - InputSection采用受控组件模式，状态由父组件管理
- **本地状态优先** - 使用React useState进行简单状态管理
- **状态机模式** - 应用状态使用状态机模式 (`IDLE` → `INPUT_VALID` → `PROCESSING` → `SUCCESS`/`ERROR`)

### 组件设计原则

- **单一职责** - 每个组件只负责一个功能
- **可复用性** - 基于shadcn/ui构建可复用组件
- **类型安全** - 严格的TypeScript类型定义
- **无障碍性** - 遵循WCAG 2.1无障碍标准

## 🎨 设计系统

项目基于**Rondo设计系统**构建，包含：

- **色彩系统** - Linear风格的紫色主题配色
- **字体系统** - Geist Sans & Mono字体家族
- **间距系统** - 基于8px网格的间距规范
- **组件库** - 统一的UI组件和交互规范

## 🔧 开发工具配置

### VSCode推荐扩展

```json
{
  "recommendations": [
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode", 
    "ms-vscode.vscode-typescript-next",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense"
  ]
}
```

### 调试配置

```json
{
  "type": "node",
  "request": "launch",
  "name": "Next.js: debug server-side",
  "program": "${workspaceFolder}/node_modules/.bin/next",
  "args": ["dev"],
  "cwd": "${workspaceFolder}"
}
```

## 📚 相关文档

- [Next.js 文档](https://nextjs.org/docs) - Next.js功能和API
- [Tailwind CSS 文档](https://tailwindcss.com/docs) - CSS框架使用指南
- [shadcn/ui 文档](https://ui.shadcn.com/) - 组件库使用指南
- [TypeScript 手册](https://www.typescriptlang.org/docs/) - TypeScript语言指南

## 🤝 贡献指南

1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../../LICENSE) 文件了解详情。

## 🆘 问题反馈

如果遇到问题或有功能建议，请：

1. 查看 [常见问题](./docs/FAQ.md)
2. 搜索现有的 [Issues](../../issues)
3. 创建新的Issue并提供详细信息

---

<div align="center">
  <strong>🎬 让AI为你的视频脚本赋能！</strong>
</div>
