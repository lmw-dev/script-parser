# 项目命名规范

## 1. TypeScript / JavaScript 命名规范 (Web项目)

### 1.1 代码标识符 (变量、函数等)
- **变量、函数、Props、方法:** 使用 `camelCase`
- **类、接口、类型别名、枚举:** 使用 `PascalCase`  
- **常量 (可重用的硬编码值):** 使用 `UPPER_CASE_SNAKE_CASE`

### 1.2 文件命名
- **Next.js 特殊文件:** 使用 `lowercase`
  - 必需: `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, `route.ts`
- **React 组件文件:** 使用 `PascalCase.tsx`
  - 定义: 如果文件的**主要默认导出**是React组件，则视为组件文件
- **类型定义文件:** `kebab-case.types.ts`
  - 定义: 仅包含 `type` 或 `interface` 导出的文件
- **其他代码文件 (hooks, utils, services):** 使用 `kebab-case.ts`

### 1.3 API 路由文件
- **Next.js App Router API 路由:** 必须命名为 `route.ts` 并放置在描述性的API路径文件夹中

## 2. 当前项目文件结构符合性检查

### ✅ 符合规范的文件
- `app/page.tsx` - Next.js特殊文件，lowercase ✓
- `app/layout.tsx` - Next.js特殊文件，lowercase ✓
- `types/index.ts` - 类型定义文件，应为 `script-parser.types.ts` 
- `lib/validation.ts` - 工具文件，kebab-case ✓
- `lib/api-client.ts` - 工具文件，kebab-case ✓

### 🔄 需要调整的文件
- `components/sections/input-section.tsx` → `components/sections/InputSection.tsx` (React组件文件)
- `components/sections/processing-section.tsx` → `components/sections/ProcessingSection.tsx`
- `components/sections/result-section.tsx` → `components/sections/ResultSection.tsx`
- `components/sections/error-section.tsx` → `components/sections/ErrorSection.tsx`
- `types/index.ts` → `types/script-parser.types.ts` (类型定义文件)

## 3. TypeScript 最佳实践应用

### 当前代码质量检查
- ✅ 严格类型安全 - 无 `any` 类型使用
- ✅ 使用 `type` 定义对象形状
- ✅ 利用类型推断
- ✅ 使用具体和精确的类型
- ✅ 强制不可变性 - 使用 `readonly`

### 建议的改进
1. 将组件文件重命名为 PascalCase
2. 将类型文件重命名为 kebab-case.types.ts
3. 确保所有导入路径更新
4. 维护现有的良好TypeScript实践
