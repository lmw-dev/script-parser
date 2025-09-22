---
inclusion: always
---
# Rule: High-Efficiency Cursor AI Prompt Design Guide  (v2.1 - Test-First Edition)



## AI Action
When prompted to generate a final "AI Instruction Prompt" for a task, your primary action is to **create a new Markdown file**.
- **File Location**: The new file **must** be saved in the `/docs/prompts/` directory at the monorepo root.
- **File Naming**: The filename **must** follow the format: `[Task-ID].prompt.[task-title-in-kebab-case].md`
  - **Example**: `TOM-199.prompt.user-authentication-system.md`

The content of this new file must follow the standard prompt structure template below.
---

# 高效Cursor AI Prompt设计指南

## 🎯 核心原则 (Core Principles)

### 1. 明确性原则 (Clarity Principle)
- **目标明确**: 每个prompt必须有清晰的目标和验收标准
- **指令具体**: 避免模糊表述，使用具体的技术术语和要求
- **上下文完整**: 提供充分的背景信息和依赖关系

### 2. 结构化原则 (Structure Principle)
- **统一格式**: 所有prompt遵循统一的结构模板
- **层次清晰**: 使用标题、子标题和列表组织内容
- **逻辑顺序**: 严格遵循“**测试 -> 实现 -> 验证**”的顺序

### 3. 可操作性原则 (Actionability Principle)
- **步骤明确**: 提供清晰的实现步骤和优先级
- **示例丰富**: 包含代码示例、接口定义和测试用例
- **检查清单**: 提供完成检查清单确保质量

## 📋 标准Prompt结构模板

### 必需部分 (Required Sections)

#### 1. 目标部分 (🎯 Objective)
`## 🎯 目标 (Objective)`
`**Linear Issue**: [任务ID] - [任务标题]`
`**核心指令**: [一句话描述要完成的核心任务，强调测试先行]`

#### 2. 上下文参考 (📋 Context References)
`## 📋 上下文参考 (Context References)`

`### 主要操作文件`
`- 核心文件: @path/to/main-file.ts (待创建/已存在)`
`- 测试文件: @path/to/main-file.test.ts (待创建)`

`### 需要遵循的内部规则`
`- @.cursor/rules/130-spec-testing-guide.mdc`
`- @.cursor/rules/[...其他相关规则]`

#### 3. 具体要求与约束 (🔧 Requirements & Constraints)
`## 🔧 具体要求与约束 (Requirements & Constraints)`

`### 技术栈约束`
`- **语言**: TypeScript (strict mode)`
`- **测试框架**: Vitest + React Testing Library`

`### 功能要求`
`[详细的功能规范和约束条件]`

`### 类型安全要求 (🛡️ Type Safety)`
`- **类型优先设计**: 先定义完整的TypeScript接口，再编写测试和实现。`

#### 4. 期望输出结构 (📝 Expected Output Structure)
`## 📝 期望输出结构 (Expected Output Structure)`

`### 4.1 测试文件结构 (e.g., /path/to/file.test.ts)`
`// 提供具体的、可执行的测试用例代码骨架`
`import { describe, it, expect } from 'vitest';`
`import { functionToTest } from './file-to-test';`

`describe('functionToTest', () => {`
`  it('should handle case A correctly', () => {`
`    // expect(...).toBe(...);`
`  });`
`});`


`### 4.2 核心实现文件结构 (e.g., /path/to/file.ts)`
`// 提供函数签名、类结构或接口定义`
`export const functionToTest = (param: Type): ReturnType => {`
`  // Implementation goes here`
`};`

---
**(关键流程变更)**
---

#### 5. 测试策略 (🧪 Testing Strategy) **(第一步执行)**
`## 🧪 测试策略 (Testing Strategy)`
`### 本任务主要测试类型: [单元测试 / 组件测试 / 集成测试]`

`### 5.1 单元测试 (Unit Tests)`
`#### 目标: 验证独立的、无副作用的纯函数逻辑。`
`#### AI执行要求 (如果适用):`
`- [ ] **创建测试文件 `*.test.ts`。**`
`- [ ] **编写失败的单元测试，覆盖所有业务逻辑分支和边界条件。**`
`- [ ] **运行测试，确认失败。**`

`### 5.2 组件测试 (Component Tests)`
`#### 目标: 验证React组件的渲染、交互和props传递是否正确。`
`#### AI执行要求 (如果适用):`
`- [ ] **创建测试文件 `*.test.tsx`。**`
`- [ ] **Mock所有外部依赖 (如hooks, API客户端)。**`
`- [ ] **编写失败的组件测试，覆盖核心渲染场景和用户交互 (点击、输入等)。**`
`- [ ] **运行测试，确认失败。**`

`### 5.3 集成测试 (Integration Tests)`
`#### 目标: 验证多个组件或模块之间的数据流和协作是否正确。`
`#### AI执行要求 (如果适用):`
`- [ ] **创建测试文件 `*.spec.tsx`。**`
`- [ ] **模拟API层，测试从用户输入到状态更新再到UI响应的完整闭环。**`
`- [ ] **编写失败的集成测试，覆盖关键的用户工作流。**`
`- [ ] **运行测试，确认失败。**`

#### 6. 实现步骤 (🔄 Implementation Steps) **(第二步执行)**
`## 🔄 实现步骤 (Implementation Steps)`

`### AI执行要求 (强制性)`
`- [ ] **第4步: 编写功能代码，其唯一目标是让所有先前编写的单元测试 100% 通过。**`
`- [ ] **第5步: 反复运行测试，直到所有测试用例全部通过。**`

---

#### 7. 完成检查清单 (🎉 Completion Checklist)
`## 🎉 完成检查清单 (Completion Checklist)`

`### Ⅰ. 功能与质量检查 (AI必须执行)`
`- [ ] 是否严格遵循了“测试先行”的流程？`
`- [ ] **单元测试是否已编写完成并100%通过？**`
`- [ ] **核心业务逻辑的测试覆盖率是否达到标准？**`
`- [ ] 是否遵循了错误处理规范？`
`- [ ] 是否为所有新增的公共接口编写了文档字符串(TSDoc/Docstrings)？`

`### Ⅱ. 构建与验证检查 (AI必须执行)`
`- [ ] **Lint检查是否通过 (`pnpm run lint`)？**`
`- [ ] **TypeScript类型检查是否通过 (`tsc --noEmit`)？**`
`- [ ] **生产构建是否成功 (`pnpm run build`)？**`

`### Ⅲ. 流程与交付检查 (AI在最后一步执行)`
`- [ ] **Git Commit Message是否已按`210-wf-git-commit.mdc`规范生成？**`
`- [ ] **是否已将所有相关文档（Dev/Task/Prompt）链接到Linear Issue的评论中？**`