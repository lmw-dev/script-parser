# TOM-319: 构建多页面分析与结果展示流程 - 史诗作战计划

- **Status**: 🎯 Designing

---

## 1. 🎯 核心目标与决策摘要 (Objective & Decision Summary)

- **所属项目 (Project)**: `[Q4/KR2] "Script Parse"MVP构建`
- **核心价值 (Core Value)**: 将单页应用重构为多页面流程，优化用户体验，为长耗时API请求提供清晰的视觉反馈和流畅的页面导航。
- **关键决策 (Core Decisions)**:
    1. **[架构模式]**: 采用 Next.js App Router 进行页面路由管理，实现首页 → 处理页 → 结果页的流程。
    2. **[状态管理]**: 基于现有架构，使用 React Context + useReducer 进行页面间状态管理，保持与现有代码风格一致。
    3. **[用户体验]**: 实现即时页面跳转，将API调用延迟到处理页面，提供清晰的等待反馈。
- **预估时间 (Time Estimate)**: ~2-3 developer-days

---

## 2. 🏗️ 技术设计与架构 (Technical Design & Architecture)

- **核心工作流 (Core Workflow)**:

    ```mermaid
    graph TD
        A[首页 /] --> B{用户提交}
        B --> C[保存输入到状态]
        C --> D[立即跳转到 /processing]
        D --> E[从状态获取输入]
        E --> F[调用 /api/parse API]
        F --> G{API响应}
        G -->|成功| H[保存结果到状态]
        G -->|失败| I[显示错误页面]
        H --> J[自动跳转到 /result]
        J --> K[从状态获取结果]
        K --> L[展示 ResultSection]
        I --> M[显示 ErrorSection]
    ```

- **页面路由结构 (Page Routes)**:

    ```typescript
    // 页面路由定义
    /                    // 首页 - 输入页面
    /processing          // 处理页 - 等待和API调用
    /result             // 结果页 - 展示分析结果
    ```

- **状态管理 (State Management)**:

    ```typescript
    // 基于现有架构的状态结构
    interface AppContextState {
      // 页面状态
      currentPage: 'home' | 'processing' | 'result';
      // 输入数据
      inputData: {
        type: 'url' | 'file';
        url?: string;
        file?: File;
      } | null;
      // 分析结果
      analysisResult: AnalysisResult | null;
      // 错误状态
      error: string | null;
      // 处理步骤
      processingStep: number;
    }

    // Context Actions
    type AppContextAction = 
      | { type: 'SET_INPUT_DATA'; payload: InputData }
      | { type: 'SET_ANALYSIS_RESULT'; payload: AnalysisResult }
      | { type: 'SET_ERROR'; payload: string }
      | { type: 'SET_PROCESSING_STEP'; payload: number }
      | { type: 'NAVIGATE_TO_PROCESSING' }
      | { type: 'NAVIGATE_TO_RESULT' }
      | { type: 'RESET' };
    ```

### 2.1 关键技术方案 (Key Technical Solutions)

> #### **页面路由管理 (`Next.js App Router`)**
>
> ```typescript
> // 使用 Next.js 13+ App Router
> app/
>   ├── page.tsx              // 首页 (/)
>   ├── processing/
>   │   └── page.tsx          // 处理页 (/processing)
>   └── result/
>       └── page.tsx          // 结果页 (/result)
> ```

> #### **状态管理 (`React Context + useReducer`)**
> ```typescript
> // 基于现有架构的 Context 实现
> const AppContext = createContext<{
>   state: AppContextState;
>   dispatch: Dispatch<AppContextAction>;
> } | null>(null);
> 
> // Context Provider 组件
> export function AppProvider({ children }: { children: React.ReactNode }) {
>   const [state, dispatch] = useReducer(appReducer, initialState);
>   return (
>     <AppContext.Provider value={{ state, dispatch }}>
>       {children}
>     </AppContext.Provider>
>   );
> }
> 
> // 自定义 Hook
> export function useAppContext() {
>   const context = useContext(AppContext);
>   if (!context) {
>     throw new Error('useAppContext must be used within AppProvider');
>   }
>   return context;
> }
> ```

> #### **页面跳转逻辑 (`Navigation Flow`)**
> ```typescript
> // 首页提交处理
> const handleSubmit = (inputData: InputData) => {
>   dispatch({ type: 'SET_INPUT_DATA', payload: inputData });
>   dispatch({ type: 'NAVIGATE_TO_PROCESSING' });
>   router.push('/processing');
> };
> 
> // 处理页API调用
> const processAnalysis = async () => {
>   try {
>     const result = await apiClient.parseVideo(state.inputData);
>     dispatch({ type: 'SET_ANALYSIS_RESULT', payload: result });
>     dispatch({ type: 'NAVIGATE_TO_RESULT' });
>     router.push('/result');
>   } catch (error) {
>     dispatch({ type: 'SET_ERROR', payload: error.message });
>   }
> };
> ```

---

## 3. 🚀 作战序列 (Implementation Sequence)

- [ ] **1. `[Web] 创建 React Context 状态管理`**: 基于现有架构，实现 AppContext 和 useReducer 进行页面间状态管理。
- [ ] **2. `[Web] 设置 Next.js App Router 页面结构`**: 创建 /processing 和 /result 页面路由，保持与现有代码风格一致。
- [ ] **3. `[Web] 重构首页输入逻辑`**: 修改现有 InputSection 组件，集成 Context 状态管理和页面跳转。
- [ ] **4. `[Web] 创建处理页面`**: 实现 /processing 页面，包含 API 调用和状态管理逻辑。
- [ ] **5. `[Web] 创建结果页面`**: 实现 /result 页面，展示分析结果。
- [ ] **6. `[Web] 优化用户体验和页面过渡`**: 添加加载状态、页面过渡动画和用户反馈。

---

## 4. 🧪 质量与测试策略 (Quality & Testing Strategy)

- **主要测试层级**: **组件测试 (Component Test)** 和 **集成测试 (Integration Test)**
- **关键测试场景**:
    1. **页面导航测试**: 验证首页 → 处理页 → 结果页的完整流程
    2. **状态管理测试**: 验证页面间数据传递的正确性
    3. **API集成测试**: 验证处理页面的API调用和错误处理
    4. **用户体验测试**: 验证加载状态、错误提示和页面过渡效果
- **性能要求**: 页面跳转响应时间 < 200ms，API调用期间提供清晰的视觉反馈

---

## 5. ✅ 验收标准 (Acceptance Criteria)

- [ ] **页面导航功能**: 在首页提交有效视频源后，浏览器地址栏变为 `/processing`
- [ ] **API调用验证**: 在 `/processing` 页面，网络面板中可以看到对 `/api/parse` 的 POST 请求
- [ ] **成功流程**: 使用 Mock API，请求成功后浏览器地址栏自动变为 `/result`
- [ ] **结果展示**: `/result` 页面成功渲染 `ResultSection` 并展示正确的模拟分析数据
- [ ] **错误处理**: 使用 Mock API，请求失败后 `/processing` 页面显示 `ErrorSection`
- [ ] **状态管理**: 页面间数据传递正确，无数据丢失或状态混乱
- [ ] **用户体验**: 页面跳转流畅，加载状态清晰，错误提示友好
- [ ] **代码质量**: 通过所有代码质量检查，测试覆盖率达到要求
