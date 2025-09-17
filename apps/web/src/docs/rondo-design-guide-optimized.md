## 2. 色彩规范 (Color Palette)
- **主色 (Primary):**
    - `brand-blue: #3B82F6` (用于按钮、链接、焦点状态等关键交互元素)
- **中性色 (Neutral):**
    - `gray-900: #111827` (用于主标题和正文)
    - `gray-600: #4B5563` (用于副标题和提示文字)
    - `gray-300: #D1D5DB` (用于边框)
    - `gray-100: #F3F4F6` (用于区域背景，如AI分析卡片)
    - `white: #FFFFFF` (用于页面主背景)
- **功能色 (Functional):**
    - `error-red: #EF4444` (用于错误提示)
    - `success-green: #10B981` (用于成功状态)
    - `warning-yellow: #F59E0B` (用于警告提示)
    - `info-blue: #3B82F6` (用于信息提示，复用主色)


## 6. 状态与交互规范 (States & Interactions)
- **加载状态 (Loading):**
    - **进度条:** 高度 `4px`, 背景色 `gray-100`, 进度色 `brand-blue`
    - **骨架屏:** 背景色 `gray-100`, 动画 `pulse` 效果
- **悬停状态 (Hover):**
    - **按钮:** 背景色加深 `10%` 透明度
    - **卡片:** 添加 `shadow-md` 阴影效果
- **焦点状态 (Focus):**
    - **所有交互元素:** `2px` `brand-blue` 外边框，`4px` 偏移

## 7. 动效规范 (Animation Guidelines)
- **过渡时长 (Duration):**
    - **快速交互:** `150ms` (按钮悬停、焦点状态)
    - **内容切换:** `300ms` (页面状态变化)
    - **"魔法时刻":** `500ms` (结果页面渐入)
- **缓动函数 (Easing):**
    - **标准:** `ease-out` (大部分交互)
    - **弹性:** `cubic-bezier(0.34, 1.56, 0.64, 1)` (成功状态)

## 8. 响应式设计 (Responsive Design)
- **断点 (Breakpoints):**
    - `mobile`: `< 768px`
    - `tablet`: `768px - 1024px`
    - `desktop`: `> 1024px`
- **移动端适配:**
    - **字号调整:** H1 `28px`, H2 `20px`, Body `16px`
    - **间距压缩:** 主要间距减少 `25%`
    - **触摸目标:** 最小 `44px` 高度

## 9. 可访问性规范 (Accessibility Guidelines)
- **对比度要求:**
    - **正文文字:** 最低 `4.5:1` 对比度
    - **大标题:** 最低 `3:1` 对比度
- **键盘导航:**
    - **Tab 顺序:** 逻辑清晰的焦点流
    - **快捷键:** `Enter` 确认，`Escape` 取消
- **屏幕阅读器:**
    - **语义化标签:** 使用正确的 HTML 语义
    - **ARIA 标签:** 为复杂交互添加描述

## 10. 组件扩展规范 (Extended Component Styles)
- **进度指示器 (Progress Indicator):**
    - **3阶段进度:** 每阶段 `33.33%` 宽度
    - **活跃状态:** `brand-blue` 背景，`white` 文字
    - **完成状态:** `success-green` 背景，勾选图标
- **错误处理 (Error Handling):**
    - **错误卡片:** 背景色 `#FEF2F2`, 边框 `error-red`
    - **重试按钮:** 次要按钮样式，`error-red` 边框
- **结果展示 (Result Display):**
    - **左右分栏:** 桌面端 `50/50` 分割，移动端垂直堆叠
    - **代码块:** 背景色 `gray-900`, 文字 `gray-100`, 圆角 `rounded-md`
