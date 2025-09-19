# TOM-319: 构建多页面分析与结果展示流程 - 史诗作战计划

- **Status**: 🎯 Designing

---

## 1. 🎯 核心目标与决策摘要 (Objective & Decision Summary)

- **所属项目 (Project)**: `[Q4/KR2] "Script Parse"MVP构建`
- **核心价值 (Core Value)**: 将单页应用重构为多页面流程，优化用户体验，为长耗时API请求提供清晰的视觉反馈和流畅的页面导航，通过智能进度条算法提升等待体验。
- **关键决策 (Core Decisions)**:
    1. **[架构模式]**: 保持现有单页应用架构，通过条件渲染和状态机实现多页面体验，避免破坏现有组件设计。
    2. **[状态管理]**: 扩展现有的 `useState` 状态机模式，添加页面状态管理，保持与现有架构一致。
    3. **[用户体验]**: 通过状态机控制页面切换，实现类似多页面的用户体验，但保持单页应用的架构优势。
    4. **[进度条算法]**: 实现基于时间的非线性模拟进度算法，总时长48秒，分三个阶段平滑推进。
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

> #### **智能进度条算法 (`Smart Progress Algorithm`)**
> ```typescript
> // 基于时间的非线性模拟进度算法
> interface ProgressConfig {
>   totalDuration: number; // 48秒总时长
>   stages: {
>     name: string;
>     duration: number;
>     startProgress: number;
>     endProgress: number;
>     easing: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
>   }[];
> }
> 
> const progressConfig: ProgressConfig = {
>   totalDuration: 48000, // 48秒
>   stages: [
>     {
>       name: "(1/3) 正在安全上传并解析视频...",
>       duration: 5000,    // 0-5秒
>       startProgress: 0,
>       endProgress: 20,
>       easing: 'ease-out'
>     },
>     {
>       name: "(2/3) 正在调用ASR服务，提取高质量逐字稿...",
>       duration: 35000,   // 5-40秒
>       startProgress: 20,
>       endProgress: 80,
>       easing: 'linear'
>     },
>     {
>       name: "(3/3) 正在调用LLM，进行AI结构化分析...",
>       duration: 8000,    // 40-48秒
>       startProgress: 80,
>       endProgress: 99,
>       easing: 'ease-in'
>     }
>   ]
> };
> 
> // 进度计算函数
> const calculateProgress = (elapsedTime: number): { progress: number; currentStage: number } => {
>   let cumulativeTime = 0;
>   for (let i = 0; i < progressConfig.stages.length; i++) {
>     const stage = progressConfig.stages[i];
>     if (elapsedTime <= cumulativeTime + stage.duration) {
>       const stageElapsed = elapsedTime - cumulativeTime;
>       const stageProgress = stageElapsed / stage.duration;
>       const easedProgress = applyEasing(stageProgress, stage.easing);
>       const progress = stage.startProgress + (stage.endProgress - stage.startProgress) * easedProgress;
>       return { progress: Math.min(progress, 99), currentStage: i + 1 };
>     }
>     cumulativeTime += stage.duration;
>   }
>   return { progress: 99, currentStage: progressConfig.stages.length };
> };
> ```

> #### **进度条实现 (`Progress Bar Implementation`)**
> ```typescript
> // 在 ProcessingSection 组件中实现进度条逻辑
> const ProcessingSection = ({ onComplete }: { onComplete: () => void }) => {
>   const [progress, setProgress] = useState(0);
>   const [currentStage, setCurrentStage] = useState(1);
>   const [startTime] = useState(Date.now());
> 
>   useEffect(() => {
>     const updateProgress = () => {
>       const elapsedTime = Date.now() - startTime;
>       const { progress: newProgress, currentStage: newStage } = calculateProgress(elapsedTime);
>       
>       setProgress(newProgress);
>       setCurrentStage(newStage);
>       
>       // 如果进度达到99%，停止更新，等待API完成
>       if (newProgress >= 99) {
>         return;
>       }
>       
>       // 继续更新进度
>       requestAnimationFrame(updateProgress);
>     };
> 
>     const animationId = requestAnimationFrame(updateProgress);
>     return () => cancelAnimationFrame(animationId);
>   }, [startTime]);
> 
>   // 当API完成时，立即设置进度为100%
>   useEffect(() => {
>     if (apiCompleted) {
>       setProgress(100);
>       setTimeout(() => onComplete(), 500); // 延迟500ms后跳转
>     }
>   }, [apiCompleted, onComplete]);
> 
>   return (
>     <div className="space-y-6">
>       <Progress value={progress} className="w-full h-3" />
>       <div className="text-center">
>         <p className="text-lg font-medium">{progressConfig.stages[currentStage - 1]?.name}</p>
>       </div>
>     </div>
>   );
> };
> ```

### 2.2 关键技术方案 (Key Technical Solutions)

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

- [ ] **1. `[Web] 实现智能进度条算法`**: 创建基于时间的非线性模拟进度算法，支持三阶段平滑推进。
- [ ] **2. `[Web] 增强 ProcessingSection 组件`**: 集成进度条算法，实现实时进度更新和阶段切换。
- [ ] **3. `[Web] 优化现有状态机逻辑`**: 扩展现有的状态转换逻辑，优化 PROCESSING 状态的处理流程。
- [ ] **4. `[Web] 优化 ResultSection 组件`**: 改进结果页面的展示效果，添加页面切换动画。
- [ ] **5. `[Web] 添加页面切换动画`**: 使用 CSS 过渡或 Framer Motion 实现平滑的页面切换效果。
- [ ] **6. `[Web] 性能优化和测试`**: 确保状态切换的性能，添加进度条算法的测试用例。

---

## 4. 📊 进度条技术规格 (Progress Bar Technical Specifications)

### 4.1 算法设计

- **总时长**: 48秒（略短于后端50秒性能目标）
- **更新频率**: 使用 `requestAnimationFrame` 实现60fps平滑更新
- **进度范围**: 0-99%（API完成时立即跳转到100%）

### 4.2 三阶段设计

1. **阶段1 (0-5秒)**: 视频上传与解析
   - 进度: 0% → 20%
   - 缓动: ease-out（快速开始，逐渐减速）
   - 描述: "(1/3) 正在安全上传并解析视频..."

2. **阶段2 (5-40秒)**: ASR语音识别
   - 进度: 20% → 80%
   - 缓动: linear（匀速推进，模拟长时间处理）
   - 描述: "(2/3) 正在调用ASR服务，提取高质量逐字稿..."

3. **阶段3 (40-48秒)**: LLM结构化分析
   - 进度: 80% → 99%
   - 缓动: ease-in（缓慢开始，快速结束）
   - 描述: "(3/3) 正在调用LLM，进行AI结构化分析..."

### 4.3 实现要求

- **平滑过渡**: 阶段间无缝切换，无跳跃
- **实时更新**: 基于实际经过时间计算进度
- **API同步**: API完成时立即完成进度条
- **错误处理**: API失败时停止进度条动画

## 5. 🧪 质量与测试策略 (Quality & Testing Strategy)

- **主要测试层级**: **组件测试 (Component Test)** 和 **集成测试 (Integration Test)**
- **关键测试场景**:
    1. **进度条算法测试**: 验证三阶段进度计算的准确性
    2. **页面导航测试**: 验证首页 → 处理页 → 结果页的完整流程
    3. **状态管理测试**: 验证页面间数据传递的正确性
    4. **API集成测试**: 验证处理页面的API调用和错误处理
    5. **用户体验测试**: 验证加载状态、错误提示和页面过渡效果
- **性能要求**: 页面跳转响应时间 < 200ms，进度条更新频率60fps，API调用期间提供清晰的视觉反馈

---

## 6. ✅ 验收标准 (Acceptance Criteria)

- [ ] **状态切换功能**: 在首页提交有效视频源后，应用状态从 `INPUT_VALID` 切换到 `PROCESSING`
- [ ] **进度条算法**: 进度条按照预设的三阶段算法平滑推进（0-5秒: 0-20%，5-40秒: 20-80%，40-48秒: 80-99%）
- [ ] **阶段切换**: 进度条能够正确显示三个处理阶段的描述文本和图标
- [ ] **API调用验证**: 在 `PROCESSING` 状态时，网络面板中可以看到对 `/api/parse` 的 POST 请求
- [ ] **成功流程**: 使用 Mock API，请求成功后进度条立即跳转到100%，应用状态自动切换到 `SUCCESS`
- [ ] **结果展示**: `SUCCESS` 状态时成功渲染 `ResultSection` 并展示正确的模拟分析数据
- [ ] **错误处理**: 使用 Mock API，请求失败后进度条停止动画，应用状态切换到 `ERROR` 并显示 `ErrorSection`
- [ ] **状态管理**: 状态转换正确，数据在状态间传递无丢失或混乱
- [ ] **用户体验**: 状态切换流畅，进度条动画自然，错误提示友好，页面切换动画自然
- [ ] **代码质量**: 通过所有代码质量检查，测试覆盖率达到要求，保持与现有架构一致
