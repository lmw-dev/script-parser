# TOM-318:task:实现灵活的视频输入功能 (URL与文件上传)

- **Status**: 🚧 Partial Complete

---

## 1. 🎯 Quick Decision Summary
- **Priority**: 🔴 High
- **Core Value**: 为用户提供无摩擦的视频输入体验，支持URL和文件两种模式，奠定脚本快拆应用核心用户旅程的基础。
- **Time Estimate**: ~8 hours

---

## 2. 🔑 Human-AI Division of Labor

### 👨‍💼 Human Tasks (You)
*Work requiring human thought and decision-making.*
- [x] **UI/UX Design Review:** 确认InputSection组件的视觉设计符合产品规范和用户体验要求
- [ ] **API Contract Validation:** 验证`/api/parse`端点的请求/响应格式是否满足前后端集成需求
- [x] **URL Validation Rules:** 确定支持的视频平台域名列表和URL格式验证规则
- [x] **File Upload Constraints:** 确定支持的视频文件类型、大小限制和安全策略
- [x] **Error Handling Strategy:** 定义各种错误场景的用户提示信息和处理流程
- [ ] **Write Test Cases:** 为InputSection组件和API端点创建初始测试用例
- [ ] **Final Review & Integration:** 执行完整的用户流程测试和代码审查

### 🤖 AI Tasks (AI)
*Automated execution work delegated to the AI.*
- [ ] **Backend API Implementation:** 在FastAPI协处理器中实现`/api/parse`端点，支持URL和文件上传两种模式
- [x] **Frontend Component Development:** 创建InputSection组件，包含URL输入、文件上传和状态管理逻辑
- [x] **State Management Logic:** 实现输入验证、按钮状态切换和处理状态的UI反馈
- [ ] **API Client Integration:** 创建前端API客户端，处理与后端的数据交互
- [x] **Error Handling Implementation:** 实现前端错误显示和用户反馈机制
- [x] **Documentation:** 为所有新增代码生成TSDoc和Python docstrings

---

## 3. 📦 AI Instruction Package
*This package is the final command for the AI after human prep is complete.*

- **🎯 Core Objective**:
  `Implement the flexible video input feature with URL and file upload support, including both frontend InputSection component and backend /api/parse endpoint, ensuring all acceptance criteria from Linear issue TOM-318 are met.`

- **🗂️ Context References**:
  `@/docs/development/TOM-318-dev-flexible-video-input-feature.md`
  `@/apps/web/src/app/page.tsx`
  `@/apps/coprocessor/app/main.py`
  `@.cursor/rules/020-gen-typescript-best-practices.mdc`
  `@.cursor/rules/021-gen-python-best-practices.mdc`
  `@.cursor/rules/140-spec-frontend-state-management.mdc`

- **✅ Acceptance Criteria**:
  ```
  1. InputSection组件正确渲染URL输入框、文件上传链接和提交按钮
  2. URL验证功能正常：有效URL启用提交按钮，无效URL显示错误提示
  3. 文件选择器功能正常：点击链接打开系统文件选择器
  4. API请求格式正确：
     - URL模式：POST /api/parse，Content-Type: application/json
     - 文件模式：POST /api/parse，Content-Type: multipart/form-data
  5. 状态流转正确：IDLE → INPUT_VALID → PROCESSING
  6. 提交后输入区域正确禁用并显示处理中反馈
  ```

---

## 4. 🚀 Implementation Sequence

### Phase 1: Backend Foundation ⏳
1. ⏳ 在`apps/coprocessor/app/main.py`中创建`/api/parse`端点
2. ⏳ 实现URL和文件上传的请求处理逻辑
3. ⏳ 定义请求/响应的Pydantic模型

### Phase 2: Frontend Core Component ✅
1. ✅ 创建`InputSection`组件文件
2. ✅ 实现URL输入框和验证逻辑
3. ✅ 实现文件上传触发和选择逻辑
4. ✅ 实现提交按钮状态管理

### Phase 3: Integration & State Management 🚧
1. ⏳ 创建API客户端处理前后端通信
2. ✅ 实现完整的状态流转逻辑
3. ✅ 集成错误处理和用户反馈

### Phase 4: UI Integration ✅
1. ✅ 将InputSection组件集成到主页面
2. ✅ 实现响应式布局和样式
3. ✅ 添加加载状态和处理中的UI反馈

---

## 5. 📋 Quality Checklist

- [x] 代码遵循TypeScript和Python最佳实践规范
- [x] 所有导出函数和组件包含完整的文档注释
- [x] 前端组件使用shadcn/ui组件库构建
- [x] 状态管理遵循"本地状态优先"原则
- [ ] API端点符合RESTful设计规范
- [x] 错误处理覆盖所有可能的失败场景
- [x] 用户界面提供清晰的反馈和引导
