# ScriptParser 前端架构文档

## 项目概述

ScriptParser 是一个基于 Next.js 14 的智能视频脚本分析工具，采用现代化的前端架构设计，遵循 Rondo 设计系统规范。

## 技术栈

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS v4 + Rondo 设计系统
- **组件库**: shadcn/ui
- **字体**: Geist Sans & Geist Mono
- **分析**: Vercel Analytics
- **状态管理**: React useState + 状态机模式

## 项目结构

\`\`\`
├── app/                          # Next.js App Router
│   ├── layout.tsx               # 根布局组件
│   ├── page.tsx                 # 主页面组件
│   └── globals.css              # 全局样式 (Rondo 设计系统)
├── components/                   # 组件目录
│   ├── sections/                # 页面区块组件
│   │   ├── input-section.tsx    # 输入区块
│   │   ├── processing-section.tsx # 处理进度区块
│   │   ├── result-section.tsx   # 结果展示区块
│   │   └── error-section.tsx    # 错误处理区块
│   └── ui/                      # shadcn/ui 基础组件
├── lib/                         # 工具库
│   ├── api-client.ts           # API 客户端
│   ├── validation.ts           # 输入验证逻辑
│   └── utils.ts                # 通用工具函数
├── types/                       # TypeScript 类型定义
│   └── index.ts                # 核心类型定义
├── hooks/                       # React Hooks
│   ├── use-mobile.ts           # 移动端检测
│   └── use-toast.ts            # Toast 通知
└── docs/                        # 项目文档
    └── frontend-architecture.md # 本文档
\`\`\`

## 核心架构设计

### 1. 状态机模式

应用采用状态机模式管理整体状态，包含 5 个核心状态：

\`\`\`typescript
type AppState = "IDLE" | "INPUT_VALID" | "PROCESSING" | "SUCCESS" | "ERROR"
\`\`\`

**状态转换流程：**
- `IDLE` → `INPUT_VALID`: 用户输入有效内容
- `INPUT_VALID` → `PROCESSING`: 用户点击开始分析
- `PROCESSING` → `SUCCESS`: 分析成功完成
- `PROCESSING` → `ERROR`: 分析过程出错
- `SUCCESS/ERROR` → `IDLE`: 用户重置应用

### 2. 组件架构

#### 主页面组件 (`app/page.tsx`)
- **职责**: 状态管理、组件协调、业务逻辑
- **特点**: 作为容器组件，不包含具体 UI 实现
- **状态**: 管理应用全局状态、处理步骤、结果数据、错误信息

#### 区块组件 (`components/sections/`)

**InputSection (输入区块)**
- **职责**: 处理用户输入（URL 或文件上传）
- **功能**: 
  - 实时输入验证
  - 文件上传处理
  - 输入状态反馈
- **验证规则**: 
  - URL: 支持抖音、小红书等平台链接
  - 文件: 支持 MP4、MOV、AVI、MKV、WEBM 格式，最大 100MB

**ProcessingSection (处理进度区块)**
- **职责**: 展示三阶段处理进度
- **功能**: 
  - 动态进度指示
  - 阶段性状态描述
  - 加载动画效果
- **处理阶段**:
  1. 视频上传与解析
  2. ASR 语音识别
  3. LLM 结构化分析

**ResultSection (结果展示区块)**
- **职责**: 展示分析结果
- **布局**: 左右分栏设计
  - 左侧: 完整逐字稿
  - 右侧: AI 结构化分析 (Hook/Core/CTA)
- **功能**: 
  - 内容复制
  - Markdown 导出
  - 重新分析

**ErrorSection (错误处理区块)**
- **职责**: 错误状态展示和恢复
- **功能**: 
  - 友好的错误提示
  - 重试操作
  - 状态重置

### 3. 数据流设计

\`\`\`
用户输入 → 验证 → API 调用 → 状态更新 → UI 渲染
    ↓         ↓        ↓         ↓         ↓
InputSection → lib/validation → lib/api-client → useState → 对应 Section
\`\`\`

### 4. 类型系统

**核心类型定义** (`types/index.ts`):

\`\`\`typescript
// 应用状态
type AppState = "IDLE" | "INPUT_VALID" | "PROCESSING" | "SUCCESS" | "ERROR"

// 视频解析请求
interface VideoParseRequest {
  type: "url" | "file"
  content: string | File
}

// 分析结果
interface AnalysisResult {
  transcript: string
  analysis: {
    hook: string
    core: string
    cta: string
  }
}

// API 响应
interface ApiResponse<T> {
  success: boolean
  result?: T
  message?: string
}
\`\`\`

## 设计系统集成

### Rondo 设计系统

**色彩系统**:
- 主色: `#3B82F6` (brand-blue)
- 中性色: 灰色系列 (`#111827`, `#4B5563`, `#D1D5DB`, `#F3F4F6`, `#FFFFFF`)
- 功能色: `#EF4444` (error-red)

**字体系统**:
- 主字体: Geist Sans
- 等宽字体: Geist Mono

**间距与圆角**:
- 基础单位: 4px
- 卡片圆角: 6px
- 按钮圆角: 8px

### 响应式设计

- **移动优先**: 采用移动优先的响应式设计策略
- **断点系统**: 使用 Tailwind CSS 标准断点
- **组件适配**: 所有组件支持移动端和桌面端

## 性能优化

### 1. 代码分割
- 使用 Next.js 自动代码分割
- 组件按需加载

### 2. 资源优化
- 图片使用 Next.js Image 组件
- 字体预加载优化

### 3. 状态管理
- 避免不必要的重渲染
- 合理使用 React.memo 和 useMemo

## 开发规范

### 1. 文件命名
- 组件文件: kebab-case (如 `input-section.tsx`)
- 类型文件: camelCase (如 `index.ts`)
- 工具文件: kebab-case (如 `api-client.ts`)

### 2. 组件设计原则
- **单一职责**: 每个组件只负责一个功能
- **可复用性**: 组件设计考虑复用场景
- **类型安全**: 严格的 TypeScript 类型定义

### 3. 状态管理原则
- **最小状态**: 只存储必要的状态
- **状态提升**: 共享状态提升到合适的父组件
- **不可变更新**: 使用不可变的方式更新状态

## 扩展性考虑

### 1. 组件扩展
- 区块组件可独立扩展功能
- UI 组件库支持主题定制

### 2. 功能扩展
- API 客户端支持多种后端服务
- 验证系统支持新的输入类型

### 3. 国际化准备
- 文案集中管理
- 组件支持多语言切换

## 部署与监控

### 1. 部署策略
- Vercel 平台部署
- 自动化 CI/CD 流程

### 2. 性能监控
- Vercel Analytics 集成
- 核心 Web 指标监控

### 3. 错误监控
- 客户端错误捕获
- 用户行为分析

## 总结

ScriptParser 前端架构采用现代化的技术栈和设计模式，具有良好的可维护性、可扩展性和用户体验。通过状态机模式管理复杂的业务流程，通过组件化设计实现代码复用，通过 TypeScript 确保类型安全，通过 Rondo 设计系统保证视觉一致性。
