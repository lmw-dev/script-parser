# TOM-326:task:实现 /api/parse 核心端点以完成分析工作流

- **Status**: 🔄 Preparing

---

## 1. 🎯 Quick Decision Summary
- **Priority**: 🔴 High (Urgent)
- **Core Value**: 构建核心后端API端点，完成"视频源获取 -> ASR转录 -> LLM分析"的完整工作流，为用户提供端到端的视频分析服务。
- **Time Estimate**: ~12 hours

---

## 2. 🔑 Human-AI Division of Labor

### 👨‍💼 Human Tasks (You)
*Work requiring human thought and decision-making.*
- [ ] **API Contract Validation**: 验证`/api/parse`端点的请求/响应格式是否满足前后端集成需求
- [ ] **ASR Service Configuration**: 配置阿里云通义听悟的API密钥和服务参数
- [ ] **LLM Service Configuration**: 配置DeepSeek和Kimi的API密钥和切换策略
- [ ] **Performance Testing**: 验证1分钟视频在50秒内完成处理的性能要求
- [ ] **Error Handling Strategy**: 定义各种错误场景的响应格式和处理流程
- [ ] **Environment Variables Setup**: 配置生产环境的环境变量和服务密钥
- [ ] **Final Integration Testing**: 执行完整的前后端集成测试和用户流程验证

### 🤖 AI Tasks (AI)
*Automated execution work delegated to the AI.*
- **Backend API Implementation**: 在FastAPI协处理器中实现`/api/parse`端点，支持URL和文件上传两种模式
- **Video Source Processing**: 实现URL解析和文件保存逻辑，支持抖音、小红书等平台链接
- **ASR Service Integration**: 集成阿里云通义听悟服务，实现视频到文本的转录功能
- **LLM Adapter Implementation**: 实现适配器模式的LLM服务，支持DeepSeek和Kimi的配置化切换
- **Response Assembly**: 实现结果组装逻辑，将逐字稿和分析结果组合成统一JSON响应
- **Resource Cleanup**: 实现临时文件清理机制，确保资源不泄露
- **Error Handling**: 实现完整的错误处理和异常响应机制
- **Documentation**: 为所有新增代码生成Python docstrings和类型注解

---

## 3. 📦 AI Instruction Package
*This package is the final command for the AI after human prep is complete.*

- **🎯 Core Objective**:
  `Implement the /api/parse endpoint in FastAPI coprocessor to handle video analysis workflow, supporting both URL and file upload modes, with complete ASR transcription and LLM analysis integration.`

- **🗂️ Context References**:
  `@/docs/development/TOM-326-dev-api-parse-core-endpoint.md`
  `@/apps/coprocessor/app/main.py`
  `@/apps/coprocessor/requirements.txt`
  `@/apps/coprocessor/.env.example`

- **✅ Acceptance Criteria**:
  ```
  1. POST /api/parse端点正确处理URL和文件上传两种输入模式
  2. 实现完整的视频处理工作流：视频源获取 -> ASR转录 -> LLM分析
  3. 集成阿里云通义听悟ASR服务，支持视频直接转录
  4. 实现LLM服务适配器，支持DeepSeek和Kimi的配置化切换
  5. 返回统一JSON格式响应，包含逐字稿和结构化分析结果
  6. 实现完整的错误处理：400/503/502/500等状态码
  7. 确保临时文件在请求完成后被正确清理
  8. 1分钟视频的端到端处理时间不超过50秒
  ```

---

## 4. 🚀 Implementation Sequence

### Phase 1: API基础架构 🔄
1. 🔄 在`apps/coprocessor/app/main.py`中创建`/api/parse`端点
2. 🔄 实现双模式输入处理（URL和文件上传）
3. 🔄 定义请求/响应的Pydantic模型

### Phase 2: 服务模块开发 🔄
1. 🔄 创建视频源处理服务（URL解析和文件保存）
2. 🔄 实现阿里云ASR服务集成
3. 🔄 实现LLM服务适配器（DeepSeek + Kimi）

### Phase 3: 工作流集成 🔄
1. 🔄 实现完整的视频分析工作流
2. 🔄 实现响应组装逻辑
3. 🔄 实现资源清理机制

### Phase 4: 错误处理与优化 🔄
1. 🔄 实现完整的错误处理和异常响应
2. 🔄 性能优化，确保50秒内完成处理
3. 🔄 添加日志和监控

### Phase 5: 测试与文档 🔄
1. 🔄 编写单元测试和集成测试
2. 🔄 完善API文档和代码注释
3. 🔄 更新环境变量配置示例

---

## 5. 📋 Quality Checklist

- [ ] 代码遵循FastAPI和Python最佳实践规范
- [ ] 所有导出函数和类包含完整的Python docstrings
- [ ] 使用Pydantic进行严格的数据验证和序列化
- [ ] API端点符合RESTful设计规范
- [ ] 错误处理覆盖所有可能的失败场景
- [ ] 实现完整的资源清理机制，防止内存和磁盘泄露
- [ ] 性能优化确保满足50秒处理时间要求
- [ ] 集成测试覆盖完整的API工作流
- [ ] 环境变量配置完整，支持生产环境部署
- [ ] 日志记录详细，便于问题排查和性能监控

---

## 6. 🔧 Technical Implementation Notes

### 6.1 Service Architecture
```python
# 推荐的服务模块结构
app/
├── services/
│   ├── video_processor.py    # 视频源处理
│   ├── asr_service.py       # 阿里云ASR服务
│   ├── llm_adapter.py       # LLM服务适配器
│   └── cleanup_service.py   # 资源清理服务
├── models/
│   ├── requests.py          # 请求模型
│   └── responses.py         # 响应模型
└── main.py                  # FastAPI应用入口
```

### 6.2 Performance Targets
- **总处理时间**: ≤50秒 (1分钟视频)
- **ASR处理**: ≤30秒
- **LLM分析**: ≤15秒
- **其他处理**: ≤5秒

### 6.3 Error Response Format
```json
{
  "success": false,
  "message": "具体错误描述",
  "error_code": "ERROR_TYPE",
  "processing_time": 1.23
}
```

### 6.4 Success Response Format
```json
{
  "success": true,
  "message": "处理成功",
  "data": {
    "transcript": "完整逐字稿内容",
    "analysis": {
      "summary": "内容摘要",
      "key_points": ["要点1", "要点2"],
      "structure": "三段式结构分析"
    }
  },
  "processing_time": 45.67
}
```

---

## 7. 🎯 Dependencies & Prerequisites

### 7.1 Required Services
- **阿里云通义听悟**: ASR服务API密钥和配置
- **DeepSeek API**: LLM服务主要提供商
- **Kimi API**: LLM服务备用提供商

### 7.2 Environment Variables
```bash
# ASR服务配置
ALIYUN_ASR_API_KEY=your_api_key
ALIYUN_ASR_API_SECRET=your_api_secret

# LLM服务配置
DEEPSEEK_API_KEY=your_deepseek_key
KIMI_API_KEY=your_kimi_key
LLM_PRIMARY_PROVIDER=deepseek

# 服务配置
MAX_FILE_SIZE=100MB
TEMP_DIR=/tmp/scriptparser
PROCESSING_TIMEOUT=50
```

### 7.3 Python Dependencies
```txt
# 需要添加到requirements.txt
aiofiles>=23.0.0
httpx>=0.24.0
python-multipart>=0.0.6
```