# TOM-320: [Epic] [Web] 实现结果复制与下载功能 - 史诗作战计划

- **Status**: ✅ Plan Approved

---

## 1. 🎯 核心目标与决策摘要 (Objective & Decision Summary)

- **所属项目 (Project)**: `[Q4/KR2] "Script Parse"MVP构建`
- **核心价值 (Core Value)**: 为用户提供高效、便捷的结果导出功能，打通AI分析结果从"查看"到"使用"的最后一公里，提升产品的实用性和用户粘性。
- **关键决策 (Core Decisions)**:
    1. **[实现方式]**: 所有复制和下载功能**必须**在客户端完成，不产生任何对后端的API请求，以确保最佳的响应速度和最低的服务器成本。
    2. **[技术选型]**: 推荐使用 `copy-to-clipboard` 库处理剪贴板操作，以保证跨浏览器的兼容性和稳定性。
- **预估时间 (Time Estimate)**: ~1 developer-day

---

## 2. 🏗️ 技术设计与架构 (Technical Design & Architecture)

- **核心工作流 (Core Workflow)**:

  ```mermaid
  graph TD
      A["用户在/result页面<br/>查看ResultSection组件"] --> B{"用户点击操作按钮"}
      B -- "点击复制按钮" --> C["1. 调用Clipboard工具函数"]
      C --> D["2. 弹出Toast提示: '复制成功!'"]
      B -- "点击下载按钮" --> E["1. 调用Markdown生成工具函数"]
      E --> F["2. 创建Blob并触发浏览器下载"]
  ```

- **API 契约 (API Contract)**: 无。本任务不涉及API变更。
- **数据模型 (Data Models)**: 无。本任务不涉及核心数据模型的变更，仅消费已有的 `AnalysisResult` 类型。

### 2.1 关键技术方案 (Key Technical Solutions)

#### **剪贴板工具函数 (`copyToClipboard`)**

建议在 `/lib/utils.ts` 中创建一个包装函数，封装 `copy-to-clipboard` 库的调用和成功/失败处理。

```typescript
import copy from 'copy-to-clipboard';

export const copyToClipboard = (text: string): boolean => {
  try {
    copy(text);
    return true;
  } catch (error) {
    console.error('Failed to copy text: ', error);
    return false;
  }
};
```

#### **Markdown生成与下载函数 (`downloadAsMarkdown`)**

建议在 `/lib/utils.ts` 中创建一个专门的函数来处理此逻辑。

```typescript
import { AnalysisResult } from '@/types';

export const downloadAsMarkdown = (result: AnalysisResult, filename: string = 'script-analysis.md') => {
  const content = `
# 视频脚本分析结果

## 完整逐字稿

${result.transcript}

## AI结构化分析

### 🚀 钩子 (Hook)

${result.analysis.hook}

### 💡 核心 (Core)

${result.analysis.core}

### 🎯 行动号召 (CTA)

${result.analysis.cta}
`;

  const blob = new Blob([content.trim()], { type: 'text/markdown;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
```

---

## 3. 🚀 作战序列 (Implementation Sequence)

*为完成此史诗任务，需要按顺序执行以下2个核心子任务 (Issues)。*

- [ ] **1. `[Web] 实现剪贴板复制功能及Toast提示`**: 在 `ResultSection` 组件中集成 `copyToClipboard` 工具函数，并为所有复制按钮绑定交互事件和成功后的Toast提示。
- [ ] **2. `[Web] 实现客户端Markdown生成与下载功能`**: 在 `ResultSection` 组件中集成 `downloadAsMarkdown` 工具函数，并为下载按钮绑定交互事件。

---

## 4. 🧪 质量与测试策略 (Quality & Testing Strategy)

- **主要测试层级**: **组件测试 (Component Test)**。
- **关键测试场景**:
    1. **复制功能测试**: 编写组件测试，模拟用户点击各个复制按钮，并**验证 `copy-to-clipboard` 库是否被以正确的文本参数调用**。
    2. **下载功能测试**: 编写组件测试，模拟用户点击下载按钮，并**验证 `downloadAsMarkdown` 函数是否被调用**。
    3. **工具函数单元测试**: 为 `downloadAsMarkdown` 函数编写单元测试，验证其能否根据输入的 `AnalysisResult` 对象，生成**内容和格式都正确的Markdown字符串**。

---

## 5. ✅ 验收标准 (Acceptance Criteria)

*只有当以下所有条件都满足时，此史诗任务才算"完成"。*

- [ ] 点击"完整逐字稿"的复制按钮，剪贴板中的内容是完整的逐字稿。
- [ ] 点击"Hook"卡片的复制按钮，剪贴板中的内容仅为Hook部分的文本。
- [ ] 每次复制操作后，页面都会出现"复制成功"的提示。
- [ ] 点击下载按钮，能成功下载一个名为 `script-analysis.md` 的文件。
- [ ] 下载的Markdown文件内容和格式，与PRD中定义的一致。
- [ ] 所有相关功能都有对应的单元或组件测试覆盖。
