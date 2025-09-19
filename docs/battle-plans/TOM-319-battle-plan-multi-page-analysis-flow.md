# TOM-319: 构建多页面分析与结果展示流程 - 史诗作战计划

- **Status**: 🎯 Designing

---

## 1. 🎯 核心目标与决策摘要 (Objective & Decision Summary)

- **所属项目 (Project)**: `[Q4/KR2] "Script Parse"MVP构建`
- **核心价值 (Core Value)**: 将单页应用重构为多页面流程，优化用户体验，为长耗时API请求提供清晰的视觉反馈和流畅的页面导航。
- **关键决策 (Core Decisions)**:
    1. **[架构模式]**: 保持现有单页应用架构，通过条件渲染和状态机实现多页面体验，避免破坏现有组件设计。
    2. **[状态管理]**: 扩展现有的 `useState` 状态机模式，添加页面状态管理，保持与现有架构一致。
    3. **[用户体验]**: 通过状态机控制页面切换，实现类似多页面的用户体验，但保持单页应用的架构优势。
- **预估时间 (Time Estimate)**: ~2-3 developer-days

---

## 2. 🏗️ 技术设计与架构 (Technical Design & Architecture)

- **核心工作流 (Core Workflow)**:

    ```mermaid
    graph TD
        A[IDLE状态 - 显示InputSection] --> B{用户提交}
        B --> C[保存输入到状态]
        C --> D[状态切换到PROCESSING]
        D --> E[显示ProcessingSection]
        E --> F[调用 /api/parse API]
        F --> G{API响应}
        G -->|成功| H[保存结果到状态]
        G -->|失败| I[状态切换到ERROR]
        H --> J[状态切换到SUCCESS]
        J --> K[显示ResultSection]
        I --> L[显示ErrorSection]
        K --> M[用户重置]
        L --> M
        M --> A
    ```

- **状态机结构 (State Machine)**:

    ```typescript
    // 扩展现有的状态机
    type AppState = "IDLE" | "INPUT_VALID" | "PROCESSING" | "SUCCESS" | "ERROR"
    
    // 页面状态映射
    const pageMapping = {
      IDLE: "InputSection",           // 输入页面
      INPUT_VALID: "InputSection",    // 输入页面（有效状态）
      PROCESSING: "ProcessingSection", // 处理页面
      SUCCESS: "ResultSection",       // 结果页面
      ERROR: "ErrorSection"           // 错误页面
    }
    ```

- **状态管理 (State Management)**:

    ```typescript
    // 扩展现有的状态结构
    const [state, setState] = useState<AppState>("IDLE")
    const [processingStep, setProcessingStep] = useState(1)
    const [result, setResult] = useState<AnalysisResult | null>(null)
    const [error, setError] = useState("")
    
    // 输入数据状态（保持现有结构）
    const [inputValue, setInputValue] = useState("")
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    
    // 状态转换函数
    const handleStateTransition = (newState: AppState) => {
      setState(newState)
      // 根据状态执行相应逻辑
      if (newState === "PROCESSING") {
        // 开始处理流程
        processAnalysis()
      }
    }
    ```

### 2.1 关键技术方案 (Key Technical Solutions)

> #### **状态机页面切换 (`State-Based Page Switching`)**
> ```typescript
> // 基于现有架构的条件渲染
> return (
>   <div className="min-h-screen bg-background">
>     {(state === "IDLE" || state === "INPUT_VALID") && (
>       <InputSection 
>         currentState={state}
>         inputValue={inputValue}
>         selectedFile={selectedFile}
>         onInputChange={handleInputChange}
>         onFileSelect={handleFileSelect}
>         onSubmit={handleSubmit}
>         error={error}
>       />
>     )}
>     {state === "PROCESSING" && (
>       <ProcessingSection step={processingStep} steps={processingSteps} />
>     )}
>     {state === "SUCCESS" && result && (
>       <ResultSection result={result} onReset={handleReset} />
>     )}
>     {state === "ERROR" && (
>       <ErrorSection error={error} onReset={handleReset} />
>     )}
>   </div>
> )
> ```

> #### **状态转换逻辑 (`State Transition Logic`)**
> ```typescript
> // 扩展现有的状态转换
> const handleSubmit = async () => {
>   setError("")
>   setState("PROCESSING")
>   setProcessingStep(1)
>   
>   try {
>     // 模拟处理步骤
>     await new Promise(resolve => setTimeout(resolve, 1000))
>     setProcessingStep(2)
>     
>     await new Promise(resolve => setTimeout(resolve, 1000))
>     setProcessingStep(3)
>     
>     // API调用
>     const result = await parseVideo(request)
>     setResult(result)
>     setState("SUCCESS")
>   } catch (err) {
>     setState("ERROR")
>     setError(err.message)
>   }
> }
> ```

> #### **用户体验优化 (`UX Enhancement`)**
> ```typescript
> // 添加页面切换动画
> const pageVariants = {
>   initial: { opacity: 0, x: 20 },
>   in: { opacity: 1, x: 0 },
>   out: { opacity: 0, x: -20 }
> }
> 
> // 使用 Framer Motion 或 CSS 过渡
> <motion.div
>   key={state}
>   initial="initial"
>   animate="in"
>   exit="out"
>   variants={pageVariants}
>   transition={{ duration: 0.3 }}
> >
>   {/* 当前页面内容 */}
> </motion.div>
> ```

---

## 3. 🚀 作战序列 (Implementation Sequence)

- [ ] **1. `[Web] 优化现有状态机逻辑`**: 扩展现有的状态转换逻辑，优化 PROCESSING 状态的处理流程。
- [ ] **2. `[Web] 增强 ProcessingSection 组件`**: 改进处理页面的视觉反馈，添加更清晰的进度指示和状态描述。
- [ ] **3. `[Web] 优化 ResultSection 组件`**: 改进结果页面的展示效果，添加页面切换动画。
- [ ] **4. `[Web] 添加页面切换动画`**: 使用 CSS 过渡或 Framer Motion 实现平滑的页面切换效果。
- [ ] **5. `[Web] 优化用户体验细节`**: 添加加载状态、错误提示和用户反馈的细节优化。
- [ ] **6. `[Web] 性能优化和测试`**: 确保状态切换的性能，添加相应的测试用例。

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

- [ ] **状态切换功能**: 在首页提交有效视频源后，应用状态从 `INPUT_VALID` 切换到 `PROCESSING`
- [ ] **API调用验证**: 在 `PROCESSING` 状态时，网络面板中可以看到对 `/api/parse` 的 POST 请求
- [ ] **成功流程**: 使用 Mock API，请求成功后应用状态自动切换到 `SUCCESS`
- [ ] **结果展示**: `SUCCESS` 状态时成功渲染 `ResultSection` 并展示正确的模拟分析数据
- [ ] **错误处理**: 使用 Mock API，请求失败后应用状态切换到 `ERROR` 并显示 `ErrorSection`
- [ ] **状态管理**: 状态转换正确，数据在状态间传递无丢失或混乱
- [ ] **用户体验**: 状态切换流畅，加载状态清晰，错误提示友好，页面切换动画自然
- [ ] **代码质量**: 通过所有代码质量检查，测试覆盖率达到要求，保持与现有架构一致
