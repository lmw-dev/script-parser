# ScriptParser AI Coprocessor

ScriptParser 项目的 AI 协处理器服务，基于 FastAPI 构建，专门负责音频转文本、视频解析和智能内容分析。

## 🎯 项目概述

AI Coprocessor 是 ScriptParser 系统的核心 AI 服务组件，采用微服务架构设计，提供以下核心功能：

- **音频转文本 (ASR)**: 集成阿里云通义听悟，支持多种音频格式
- **视频解析**: 支持 URL 和文件上传两种模式的视频处理
- **智能分析**: 集成 DeepSeek/Kimi LLM，提供文本摘要、关键词提取等功能
- **高性能 API**: 基于 FastAPI 的异步 API 服务

## 🏗️ 技术栈

- **Python** 3.12+ - 核心编程语言
- **FastAPI** 0.111+ - 高性能异步 Web 框架
- **Uvicorn** 0.29+ - ASGI 服务器
- **Pydantic** 2.7+ - 数据验证和序列化
- **python-multipart** - 文件上传支持
- **python-dotenv** - 环境变量管理
- **Ruff** - 代码检查和格式化工具

## 📁 项目结构

```
apps/coprocessor/
├── app/
│   ├── services/           # 业务服务模块
│   │   └── llm_service.py  # LLM 适配器服务
│   ├── main.py            # FastAPI 应用入口
│   └── test_main.py       # 集成测试
├── .env.example           # 环境变量模板
├── .env                   # 环境变量配置 (需要创建)
├── requirements.txt       # Python 依赖
├── pyproject.toml        # 项目配置和代码规范
├── Dockerfile            # Docker 镜像构建
└── README.md             # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.12+
- pip 或 poetry (包管理器)

### 本地开发环境搭建

1. **进入项目目录**
```bash
cd apps/coprocessor
```

2. **创建虚拟环境**
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入实际的 API 密钥
```

5. **启动开发服务器**
```bash
# 开发模式 (热重载)
python -m uvicorn app.main:app --reload --port 8000

# 或者直接运行
python app/main.py
```

6. **访问服务**
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- 根路径: http://localhost:8000/

## 📋 API 接口文档

### 健康检查

#### GET /
```bash
curl http://localhost:8000/
```
**响应:**
```json
{
  "message": "ScriptParser AI Coprocessor is running",
  "version": "1.0.0"
}
```

#### GET /health
```bash
curl http://localhost:8000/health
```
**响应:**
```json
{
  "status": "healthy",
  "service": "ai-coprocessor"
}
```

### 音频转文本

#### POST /api/audio/transcribe
```bash
curl -X POST "http://localhost:8000/api/audio/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://example.com/audio.mp3",
    "language": "zh-CN"
  }'
```
**响应:**
```json
{
  "success": true,
  "transcript": "转录的文本内容",
  "message": "Audio transcription successful"
}
```

### 文本智能分析

#### POST /api/text/analyze
```bash
curl -X POST "http://localhost:8000/api/text/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "待分析的文本内容",
    "analysis_type": "summary"
  }'
```
**响应:**
```json
{
  "success": true,
  "result": "分析结果",
  "message": "Text analysis successful"
}
```

### 视频解析 (新功能)

#### POST /api/parse - JSON 模式 (URL)
```bash
curl -X POST "http://localhost:8000/api/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/video.mp4"
  }'
```

#### POST /api/parse - 文件上传模式
```bash
curl -X POST "http://localhost:8000/api/parse" \
  -F "file=@/Users/liumingwei/01-project/12-liumw/15-script-parser/docs/data/IMG_0029.MOV"
```

**响应格式:**
```json
{
  "success": true,
  "data": {
    "transcript": "视频转录文本",
    "analysis": {}
  }
}
```

## 🔧 开发指南

### 代码规范

项目使用 **Ruff** 进行代码检查和格式化：

```bash
# 代码检查
ruff check .

# 自动修复
ruff check . --fix

# 代码格式化
ruff format .
```

### 运行测试

确保已安装测试依赖：
```bash
pip install pytest pytest-asyncio pytest-cov
# 或者重新安装所有依赖
pip install -r requirements.txt
```

运行测试：
```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest app/test_main.py

# 详细输出
python -m pytest -v

# 测试覆盖率（需要 SQLite3 支持）
# python -m pytest --cov=app

# 如果遇到 SQLite3 问题，可以先运行基本测试
python -m pytest app/test_main.py -v --tb=short
```

### 添加新的 API 端点

1. **在 `app/main.py` 中添加路由**
```python
@app.post("/api/new-endpoint")
async def new_endpoint(request: NewRequest):
    # 实现逻辑
    return {"result": "success"}
```

2. **定义 Pydantic 模型**
```python
class NewRequest(BaseModel):
    field1: str
    field2: int = 0
```

3. **编写测试**
```python
def test_new_endpoint():
    response = client.post("/api/new-endpoint", json={"field1": "test"})
    assert response.status_code == 200
```

### 添加新的服务模块

在 `app/services/` 目录下创建新的服务模块：

```python
# app/services/new_service.py
class NewService:
    def __init__(self):
        pass
    
    async def process(self, data):
        # 处理逻辑
        return result
```

## 🔐 环境变量配置

在 `.env` 文件中配置以下环境变量：

```bash
# 阿里云ASR配置
ALIYUN_ASR_API_KEY=your_aliyun_asr_api_key
ALIYUN_ASR_API_SECRET=your_aliyun_asr_api_secret

# DeepSeek LLM配置
DEEPSEEK_API_KEY=your_deepseek_api_key

# Kimi LLM配置 (备选)
KIMI_API_KEY=your_kimi_api_key

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

## 🐳 Docker 部署

### 构建镜像
```bash
docker build -t scriptparser-coprocessor .
```

### 运行容器
```bash
docker run -d \
  --name coprocessor \
  -p 8000:8000 \
  --env-file .env \
  scriptparser-coprocessor
```

### 使用 Docker Compose
```bash
# 在项目根目录
docker-compose up coprocessor
```

## 🧪 测试策略

### 测试类型

1. **单元测试**: 测试单个函数和类的功能
2. **集成测试**: 测试 API 端点的完整流程
3. **性能测试**: 验证 API 响应时间和并发处理能力

### 测试覆盖

- ✅ API 端点功能测试
- ✅ 请求验证测试
- ✅ 错误处理测试
- ✅ 响应格式测试

### 测试数据

测试使用模拟数据，不依赖外部 API 服务，确保测试的稳定性和速度。

## 📊 性能指标

### 目标性能

- **响应时间**: < 100ms (健康检查)
- **并发处理**: 支持 100+ 并发请求
- **视频处理**: 1分钟视频 < 50秒处理时间
- **内存使用**: < 512MB (基础运行)

### 监控指标

- API 响应时间
- 错误率统计
- 内存和 CPU 使用率
- 外部 API 调用延迟

## 🔄 开发工作流

### 功能开发流程

1. **需求分析**: 明确功能需求和 API 设计
2. **编写测试**: 先编写失败的测试用例 (TDD)
3. **实现功能**: 编写代码使测试通过
4. **代码审查**: 运行 ruff 检查和格式化
5. **集成测试**: 验证与其他组件的集成
6. **文档更新**: 更新 API 文档和 README

### Git 提交规范

```bash
# 功能开发
git commit -m "feat(api): add video parsing endpoint"

# 问题修复
git commit -m "fix(parse): handle empty file upload"

# 文档更新
git commit -m "docs(readme): update API documentation"

# 测试相关
git commit -m "test(parse): add integration tests for dual input modes"
```

## 🚧 开发路线图

### 当前版本 (v1.0.0)
- ✅ 基础 API 框架
- ✅ 健康检查端点
- ✅ 音频转文本接口 (模拟)
- ✅ 文本分析接口 (模拟)
- ✅ 视频解析端点骨架

### 下一版本 (v1.1.0)
- [ ] 集成阿里云 ASR API
- [ ] 实现 URL 解析模块 (抖音等平台)
- [ ] 文件上传和临时存储
- [ ] 错误重试机制

### 未来版本
- [ ] 集成 DeepSeek/Kimi LLM
- [ ] 批量处理支持
- [ ] WebSocket 实时通信
- [ ] 缓存机制优化
- [ ] 监控和日志系统

## 🐛 故障排除

### 常见问题

1. **端口占用**
```bash
# 检查端口占用
lsof -i :8000
# 杀死占用进程
kill -9 <PID>
```

2. **依赖安装失败**
```bash
# 升级 pip
pip install --upgrade pip
# 清理缓存
pip cache purge
```

3. **环境变量未生效**
```bash
# 检查 .env 文件
cat .env
# 重新加载环境
source .venv/bin/activate
```

4. **API 调用失败**
```bash
# 检查服务状态
curl http://localhost:8000/health
# 查看日志
python -m uvicorn app.main:app --reload --log-level debug
```

### 调试技巧

- 使用 `--log-level debug` 查看详细日志
- 在代码中添加 `print()` 或 `logging` 语句
- 使用 FastAPI 自动生成的文档页面测试 API
- 检查 `.env` 文件中的环境变量配置

## 📞 支持与贡献

### 获取帮助

- 查看 [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- 查看项目 Issues 页面
- 联系开发团队

### 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发规范

- 遵循 PEP 8 Python 代码规范
- 使用 Ruff 进行代码检查和格式化
- 编写完整的测试用例
- 更新相关文档
- 添加适当的类型注解

## 📄 许可证

本项目采用 MIT License 开源协议。详见 [LICENSE](../../LICENSE) 文件。