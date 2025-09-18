
## 1\. 🎯 核心目标与决策摘要 (Objective & Decision Summary)

  - **所属项目 (Project)**: `[[00 - 项目驾驶舱 - 智能脚本提取器]]`
  - **核心价值 (Core Value)**: 构建MVP的核心后端工作流，完成从“视频源”到“结构化AI洞察”的端到端价值交付，为商业模式的快速验证提供技术基础。
  - **关键决策 (Core Decisions)**:
    1.  **[API模式]**: 采用**同步阻塞API**模式，以最快的速度和最低的架构复杂度交付MVP，同时通过优化性能规避Serverless平台的60秒超时风险。
    2.  **[架构模式]**: **LLM服务**必须采用**适配器模式 (Adapter Pattern)**，以支持在 `DeepSeek` (主) 和 `Kimi` (备) 之间的灵活切换，确保服务的高可用性。
    3.  **[ASR策略]**: 直接利用**阿里云通义听悟**处理视频URL或文件的能力，**避免**在本地服务器进行FFmpeg转码，以简化架构并提升效率。
  - **预估时间 (Time Estimate)**: \~12-16小时 (约2个开发日)

-----

## 2\. 🏗️ 技术设计与架构 (Technical Design & Architecture)

  - **核心工作流 (Core Workflow)**:
    ```mermaid
    graph TD
        subgraph "Phase 1: 输入处理 (Input Handling)"
            A[POST /api/parse] --> B{输入类型?}
            B -- "URL" --> C[解析分享链接, 获取视频URL]
            B -- "文件上传" --> D[保存至临时文件路径]
        end

        subgraph "Phase 2: 核心分析 (Core Analysis)"
            C --> E[阿里云ASR服务 (Video to Text)]
            D --> E
            E --> F[LLM服务适配器 (Text to JSON)]
        end

        subgraph "Phase 3: 输出与清理 (Output & Cleanup)"
            F --> G[组合'逐字稿'与'分析结果']
            G --> H[返回最终JSON响应]
            H --> I{是否有临时文件?}
            I -- "是" --> J[删除临时文件]
            I -- "否" --> K[结束]
            J --> K
        end
    ```
  - **API 契约 (API Contract)**:
      - **Endpoint**: `POST /api/parse`
      - **Request (URL)**: `Content-Type: application/json`, Body: `{ "url": "..." }`
      - **Request (File)**: `Content-Type: multipart/form-data`
      - **Success Response (200 OK)**:
        ```json
        {
          "success": true,
          "data": {
            "transcript": "...",
            "analysis": { "hook": "...", "core": "...", "cta": "..." }
          }
        }
        ```
  - **数据模型 (Data Models)**: 将使用Pydantic模型来严格定义请求和响应的结构。

### 2.1 关键技术方案 (Key Technical Solutions)

> #### **抖音URL解析器 (`DouyinParser`)**
>
> 基于PoC验证，我们将自研此模块。核心逻辑是：
>
> ```python
> class DouyinParser:
>     def parse_share_url(self, share_text: str) -> VideoInfo:
>         # 1. 使用正则表达式从分享文本中提取出 http/https 链接
>         # 2. 发送请求并跟随302重定向，从最终URL中获取 video_id
>         # 3. 抓取PC端分享页面HTML
>         # 4. 从HTML中解析出 window._ROUTER_DATA 这个JSON对象
>         # 5. 从JSON中提取无水印视频播放地址 (playwm -> play)
> ```
>
> #### **LLM服务适配器 (`LLMAdapter`)**
>
> ```python
> class LLMService(Protocol):
>     async def analyze(self, text: str) -> AnalysisResult: ...
> ```

> class DeepSeekAdapter(LLMService): ...
> class KimiAdapter(LLMService): ...

> class LLMRouter:
> def **init**(self, primary: str = "deepseek"): ...
> async def analyze(self, text: str):
> try:
> \# 尝试主服务
> except Exception:
> \# 切换到备用服务
>
> ```
> ```

-----

## 3\. 🚀 作战序列 (Implementation Sequence)

*为完成此史诗任务，需要按顺序执行以下6个原子化子任务 (Issues)。*

  - [x] **1. `[Coprocessor] 创建 /api/parse 端点的基本骨架并支持双模式输入`** ✅ **已完成**: 搭建FastAPI路由，使其能正确接收并验证两种`POST`请求类型，并返回模拟响应。
  - [x] **2. `[Coprocessor] 实现并集成URL解析模块`** ✅ **已完成**: 将`ShareURLParser`的逻辑实现为一个可测试的模块，并集成到API的URL处理路径中。支持抖音和小红书平台。
  - [x] **3. `[Coprocessor] 实现临时文件处理与安全保存逻辑`** ✅ **已完成**: 建立一套健壮的机制，用于安全地接收上传的视频文件并保存到临时目录。
  - [ ] **4. `[Coprocessor] 集成阿里云通义听悟ASR服务`**: 创建一个专门的ASR客户端，调用阿里云API完成视频到文本的转换。
  - [ ] **5. `[Coprocessor] 设计并实现LLM服务适配器模式`**: 构建 `LLMRouter` 和 `DeepSeek/Kimi` 适配器，实现可配置、高可用的LLM服务。
  - [ ] **6. `[Coprocessor] 编排完整的端到端工作流并实现资源清理`**: 将所有模块串联起来，并用 `try...finally` 确保临时文件被彻底清理。

### 📊 当前进度: 3/6 子任务完成 (50%)

#### ✅ 已完成功能详情

**1. API端点基础框架 (TOM-327)**
- ✅ FastAPI `/api/parse` 端点已创建
- ✅ 支持 `application/json` 和 `multipart/form-data` 双模式输入
- ✅ 完整的请求/响应模型定义 (Pydantic)
- ✅ CORS 中间件配置
- ✅ 基础错误处理机制

**2. URL解析模块 (TOM-328)**
- ✅ `ShareURLParser` 类完整实现
- ✅ 支持抖音平台完整解析 (分享文本 + 简化URL)
- ✅ 支持小红书平台解析 (第三方API集成)
- ✅ 平台路由逻辑 (`douyin.com`, `xiaohongshu.com`)
- ✅ 完整的错误处理 (`URLParserError`, `NotImplementedError`)
- ✅ 100% 单元测试覆盖
- ✅ 已集成到 `/api/parse` 端点

**3. 临时文件处理服务 (TOM-329)**
- ✅ `FileHandler` 类完整实现
- ✅ 异步文件操作 (使用 `aiofiles`)
- ✅ 文件名安全处理 (`werkzeug.utils.secure_filename`)
- ✅ UUID唯一文件名生成防止冲突
- ✅ `TempFileInfo` 数据模型定义
- ✅ `FileHandlerError` 自定义异常处理
- ✅ 文件清理机制 (`cleanup` 静态方法)
- ✅ 100% 单元测试覆盖
- ✅ 已集成到 `/api/parse` 端点 (try...finally 清理)

**测试验证结果:**
```bash
# 抖音链接解析 - ✅ 成功
curl -X POST "http://localhost:8000/api/parse" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://v.douyin.com/ZbYltR4tOKE/"}'

# 小红书链接解析 - ✅ 成功  
curl -X POST "http://localhost:8000/api/parse" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.xiaohongshu.com/discovery/item/68c94ab0000000001202ca84"}'

# 文件上传处理 - ✅ 成功
curl -X POST "http://localhost:8000/api/parse" \
  -F "file=@docs/data/IMG_0029.MOV"
```

-----

## 4\. 🧪 质量与测试策略 (Quality & Testing Strategy)

  - **主要测试层级**: **单元测试 (Unit Tests)** 和 **集成测试 (Integration Tests)**。
  - **关键测试场景**:
    1.  **单元测试**: 必须为 `DouyinParser` 和 `LLMAdapter` 的核心逻辑编写详尽的单元测试。
    2.  **集成测试**: 必须编写一个端到端的集成测试，该测试会**模拟 (Mock)** 对阿里云和LLM的API调用，但会真实地流经我们内部的所有模块（从接收请求到返回响应）。
  - **性能要求**: 必须满足“处理1分钟视频，总耗时不超过50秒”的性能指标。

-----

## 5\. ✅ 验收标准 (Acceptance Criteria)

*只有当以下所有条件都满足时，此史诗任务才算"完成"。*

  - [x] **URL解析功能** ✅ **已完成**: 提交一个真实的抖音分享链接到 `/api/parse`，能够成功返回包含视频信息的 `200 OK` 响应。
  - [x] **文件上传处理** ✅ **已完成**: 上传一个视频文件，能够成功返回包含文件信息的 `200 OK` 响应。
  - [x] **错误处理** ✅ **已完成**: 提交一个无效的URL或文件，能够返回相应的 `4xx` 客户端错误。
  - [ ] **完整工作流**: 上传一个1分钟以内的视频文件，能够在50秒内成功返回包含"逐字稿"和"三段式分析"的 `200 OK` 响应。
  - [ ] **服务容错**: 在模拟ASR或LLM服务失败时，能够返回相应的 `5xx` 服务器端错误。
  - [x] **资源清理** ✅ **已完成**: 在服务器日志中可以确认，每次请求处理完毕后，相关的临时文件都已被删除。

### 📈 验收进度: 4/6 标准完成 (67%)