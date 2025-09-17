# 组件规格说明文档

## 概述

本文档详细描述了 ScriptParser 应用中各个组件的具体实现规格、API 接口和使用方法。

## 核心组件规格

### 1. InputSection 组件

**文件路径**: `components/sections/input-section.tsx`

**组件职责**:
- 处理用户视频输入（URL 或文件上传）
- 实时输入验证和状态反馈
- 触发分析流程

**Props 接口**:
\`\`\`typescript
interface InputSectionProps {
  onSubmit: (data: VideoParseRequest) => void
  onStateChange: (state: AppState) => void
  currentState: AppState
  error: string
}
\`\`\`

**核心功能**:
- **URL 输入验证**: 支持抖音、小红书、YouTube 等平台链接
- **文件上传**: 支持 MP4、MOV、AVI、MKV、WEBM 格式，最大 100MB
- **实时反馈**: 输入状态实时更新，按钮状态动态变化
- **错误处理**: 显示验证错误和上传错误

**验证规则**:
\`\`\`typescript
// URL 验证正则表达式
const urlPatterns = [
  /^https?:\/\/(www\.)?douyin\.com\/.+/,
  /^https?:\/\/v\.douyin\.com\/.+/,
  /^https?:\/\/(www\.)?xiaohongshu\.com\/.+/,
  /^https?:\/\/www\.youtube\.com\/watch\?v=.+/,
  /^https?:\/\/youtu\.be\/.+/
]

// 文件验证
const allowedTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm']
const maxFileSize = 100 * 1024 * 1024 // 100MB
\`\`\`

### 2. ProcessingSection 组件

**文件路径**: `components/sections/processing-section.tsx`

**组件职责**:
- 展示三阶段处理进度
- 提供视觉反馈和加载动画

**Props 接口**:
\`\`\`typescript
interface ProcessingSectionProps {
  step: number
  steps: string[]
}
\`\`\`

**处理阶段**:
1. **阶段 1**: 视频上传与解析 (2秒)
2. **阶段 2**: ASR 语音识别 (2秒)  
3. **阶段 3**: LLM 结构化分析 (2秒)

**视觉设计**:
- 进度条动画
- 步骤指示器
- 加载状态图标
- 阶段描述文本

### 3. ResultSection 组件

**文件路径**: `components/sections/result-section.tsx`

**组件职责**:
- 展示分析结果
- 提供内容操作功能

**Props 接口**:
\`\`\`typescript
interface ResultSectionProps {
  result: AnalysisResult
  onReset: () => void
  onCopy: (text: string) => void
  onDownload: () => void
}
\`\`\`

**布局设计**:
- **左侧面板**: 完整逐字稿展示
  - 可滚动文本区域
  - 复制按钮
  - 字数统计
- **右侧面板**: AI 结构化分析
  - Hook (钩子) 部分
  - Core (核心) 部分  
  - CTA (行动号召) 部分
  - 每部分独立复制功能

**功能特性**:
- **复制功能**: 支持整体和分段复制
- **导出功能**: 生成 Markdown 格式文件
- **重新分析**: 返回输入状态
- **"魔法时刻"**: 结果展示的渐入动画

### 4. ErrorSection 组件

**文件路径**: `components/sections/error-section.tsx`

**组件职责**:
- 错误状态展示
- 提供恢复操作

**Props 接口**:
\`\`\`typescript
interface ErrorSectionProps {
  error: string
  onReset: () => void
}
\`\`\`

**错误类型**:
- 网络连接错误
- 文件格式不支持
- 文件大小超限
- 服务器处理错误
- 未知错误

**用户体验**:
- 友好的错误提示
- 明确的解决建议
- 一键重试功能

## 工具库规格

### 1. 验证工具 (lib/validation.ts)

**核心函数**:

\`\`\`typescript
// URL 验证
export function validateUrl(url: string): ValidationResult

// 文件验证  
export function validateFile(file: File): ValidationResult

// 通用验证结果接口
interface ValidationResult {
  isValid: boolean
  error?: string
  type?: 'url' | 'file'
}
\`\`\`

**验证逻辑**:
- URL 格式检查
- 支持平台检测
- 文件类型验证
- 文件大小检查

### 2. API 客户端 (lib/api-client.ts)

**核心函数**:

\`\`\`typescript
// 视频解析 API
export async function parseVideo(request: VideoParseRequest): Promise<ApiResponse<AnalysisResult>>

// 模拟 API (开发阶段)
export async function mockParseVideo(request: VideoParseRequest): Promise<ApiResponse<AnalysisResult>>
\`\`\`

**API 规格**:
- RESTful API 设计
- 统一错误处理
- 请求/响应类型定义
- 超时和重试机制

## 类型系统规格

### 核心类型定义 (types/index.ts)

\`\`\`typescript
// 应用状态枚举
export type AppState = "IDLE" | "INPUT_VALID" | "PROCESSING" | "SUCCESS" | "ERROR"

// 视频解析请求
export interface VideoParseRequest {
  type: "url" | "file"
  content: string | File
  metadata?: {
    filename?: string
    size?: number
    duration?: number
  }
}

// 分析结果结构
export interface AnalysisResult {
  id: string
  timestamp: string
  transcript: string
  analysis: {
    hook: string
    core: string
    cta: string
    summary?: string
    keywords?: string[]
  }
  metadata: {
    duration: number
    wordCount: number
    confidence: number
  }
}

// API 响应包装
export interface ApiResponse<T> {
  success: boolean
  result?: T
  message?: string
  error?: {
    code: string
    details: string
  }
}

// 验证结果
export interface ValidationResult {
  isValid: boolean
  error?: string
  type?: 'url' | 'file'
  metadata?: Record<string, any>
}
\`\`\`

## 样式规格

### Rondo 设计系统集成

**CSS 变量定义** (app/globals.css):
\`\`\`css
:root {
  /* Rondo 品牌色彩 */
  --color-brand-blue: oklch(0.608 0.182 258.338); /* #3B82F6 */
  --color-error-red: oklch(0.627 0.237 25.331);   /* #EF4444 */
  
  /* 中性色系 */
  --color-gray-900: oklch(0.145 0 0);  /* #111827 */
  --color-gray-600: oklch(0.556 0 0);  /* #4B5563 */
  --color-gray-300: oklch(0.922 0 0);  /* #D1D5DB */
  --color-gray-100: oklch(0.97 0 0);   /* #F3F4F6 */
  
  /* 圆角规格 */
  --radius-card: 0.375rem;    /* 6px 卡片圆角 */
  --radius-button: 0.5rem;    /* 8px 按钮圆角 */
}
\`\`\`

**工具类定义**:
\`\`\`css
.text-brand-blue { color: var(--color-brand-blue); }
.bg-brand-blue { background-color: var(--color-brand-blue); }
.rounded-rondo-card { border-radius: var(--radius-card); }
.rounded-rondo-button { border-radius: var(--radius-button); }
\`\`\`

## 性能规格

### 组件性能要求

**渲染性能**:
- 首次渲染时间 < 100ms
- 状态切换动画 < 300ms
- 文件上传响应 < 50ms

**内存使用**:
- 组件内存占用 < 10MB
- 文件缓存限制 100MB
- 状态数据 < 1MB

**网络性能**:
- API 请求超时 30s
- 文件上传进度反馈
- 错误重试机制 (最多3次)

## 可访问性规格

### WCAG 2.1 AA 标准

**键盘导航**:
- 所有交互元素支持 Tab 导航
- 明确的焦点指示器
- 逻辑的 Tab 顺序

**屏幕阅读器**:
- 语义化 HTML 结构
- 适当的 ARIA 标签
- 状态变化通知

**色彩对比**:
- 文本对比度 ≥ 4.5:1
- 交互元素对比度 ≥ 3:1
- 错误状态明确标识

## 测试规格

### 单元测试覆盖

**组件测试**:
- 渲染测试
- 交互测试  
- 状态变化测试
- Props 验证测试

**工具函数测试**:
- 验证逻辑测试
- API 客户端测试
- 边界条件测试
- 错误处理测试

**集成测试**:
- 端到端用户流程
- 状态机转换测试
- API 集成测试

### 测试覆盖率要求

- 组件测试覆盖率 ≥ 90%
- 工具函数覆盖率 ≥ 95%
- 集成测试覆盖核心流程 100%

## 部署规格

### 构建要求

**构建产物**:
- 静态资源优化
- 代码分割
- Tree shaking
- 压缩优化

**环境配置**:
- 开发环境配置
- 生产环境配置
- 环境变量管理
- 错误监控集成

**性能指标**:
- 首屏加载时间 < 2s
- 交互响应时间 < 100ms
- Lighthouse 评分 ≥ 90

这份组件规格文档为开发团队提供了详细的实现指导，确保代码质量和用户体验的一致性。
