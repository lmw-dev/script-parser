# 抖音视频解析失败修复记录

**日期**: 2025-11-05  
**问题**: Mac mini 环境下抖音视频 URL 解析失败  
**状态**: ✅ 已解决  
**相关提交**: 
- `2e5fe1a` - fix(api): fix douyin parsing with clean client
- `ae1be80` - fix(api): use hasattr to check optional key_quotes field

---

## 问题概述

### 症状
- Mac mini 上抖音视频解析失败，返回 "从HTML中解析视频信息失败"
- 本地 MacBook 和腾讯云 VPS 环境正常
- 部署前（昨天）Mac mini 可以正常解析抖音视频

### 环境对比
| 环境 | 状态 | 说明 |
|------|------|------|
| 本地 MacBook | ✅ 正常 | 使用代理可以解析 |
| 腾讯云 VPS | ✅ 正常 | 国内服务器，无需代理 |
| Mac mini | ❌ 失败 | 通过 Tailscale 连接，解析失败 |

---

## 问题分析过程

### 1. 初步排查

**测试方法**：
```bash
# 测试各环境的网络连通性
curl -I "https://www.douyin.com"
curl -I "https://aweme.snssdk.com"
```

**结果**：所有环境均能正常访问抖音域名（HTTP/2 404）

### 2. 深入调查

通过在 Mac mini 容器内直接测试 Python httpx 库：

```python
import httpx
client = httpx.AsyncClient(headers={"User-Agent": "..."}, follow_redirects=True)
response = await client.get("https://www.iesdouyin.com/share/video/7565816808079494440")
```

**关键发现**：
- 单独测试时：HTML 长度 36,835 字节，**包含** `window._ROUTER_DATA` ✅
- API 调用时：HTML 长度 11,000+ 字节，**不包含** `window._ROUTER_DATA` ❌

### 3. 根本原因定位

#### 问题 1: HTTP 客户端会话状态污染

**原始代码逻辑**：
```python
# 第一次请求获取 video_id
share_response = await client.get(url)  
video_id = extract_video_id(share_response.url)

# 第二次请求获取页面内容（复用同一个client）
clean_url = f'https://www.iesdouyin.com/share/video/{video_id}'
page_response = await client.get(clean_url)  # ❌ 返回简化版页面
```

**问题**：
1. 第一次请求设置了 Cookie/Session 状态
2. 第二次请求复用这些状态时，服务器返回不同内容（11KB 轻量级页面）

#### 问题 2: HTTP Headers 过于完整

**测试发现**：
```python
# 使用完整 headers
headers = {
    "User-Agent": "...",
    "Accept": "text/html,application/xhtml+xml,...",
    "Accept-Language": "zh-CN,zh;q=0.8,...",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}
# 结果：返回 11KB 简化页面 ❌

# 仅使用 User-Agent
headers = {"User-Agent": "Mozilla/5.0 (iPhone...)"}
# 结果：返回 36KB 完整页面 ✅
```

**结论**：抖音服务器会根据 headers 判断客户端类型，过于完整的 headers 被识别为某种特定客户端，返回简化页面。

---

## 解决方案

### 修复 1: 使用独立客户端请求 clean URL

**修改位置**：`apps/coprocessor/app/services/url_parser.py`

```python
# 第一次请求：获取 video_id
share_response = await client.get(url)
video_id = self._extract_item_id_from_url(str(share_response.url))

# 关键修复：创建新的独立客户端
clean_url = f'https://www.iesdouyin.com/share/video/{video_id}'
simple_headers = {"User-Agent": user_agents[attempt % len(user_agents)]}

clean_client = httpx.AsyncClient(
    headers=simple_headers,      # 只使用 User-Agent
    proxies=proxies,
    timeout=httpx.Timeout(20.0, connect=10.0),
    follow_redirects=True,       # 允许重定向
    verify=False
)

try:
    page_response = await clean_client.get(clean_url)
    html_content = page_response.text
finally:
    await clean_client.aclose()
```

**关键点**：
1. ✅ 使用新的独立客户端（避免会话污染）
2. ✅ 简化 headers 只保留 User-Agent
3. ✅ 设置 `follow_redirects=True`（获取完整页面）

### 修复 2: 安全访问可选字段

**修改位置**：`apps/coprocessor/app/main.py`

```python
# 原代码（会抛出 AttributeError）
if analysis_result.analysis.key_quotes is not None:
    llm_analysis["key_quotes"] = analysis_result.analysis.key_quotes

# 修复后（安全检查）
if hasattr(analysis_result.analysis, 'key_quotes') and \
   analysis_result.analysis.key_quotes is not None:
    llm_analysis["key_quotes"] = analysis_result.analysis.key_quotes
```

**问题**：`key_quotes` 是 Pydantic 模型中的可选字段（`list[str] | None = None`），直接访问不存在的字段会抛出 `AttributeError`。

**解决**：使用 `hasattr()` 先检查字段是否存在。

---

## 测试验证

### 验证步骤

1. **提交代码**：
```bash
git commit -m "fix(api): fix douyin parsing with clean client"
git push origin main
```

2. **部署到 Mac mini**：
```bash
ssh 100.123.255.27 'cd /Volumes/ExternalLiumw/lavori/01_code/15-liumw/03-script-parse && \
  bash deploy-macmini-quick.sh'
```

3. **API 测试**：
```bash
curl -X POST http://100.123.255.27:8081/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://v.douyin.com/AuPQJ_FVvbQ/"}'
```

### 测试结果

✅ **完全成功**

```
URL 解析：     1.4 秒  ✅
ASR 转录：    18.0 秒  ✅
LLM 分析：    64.5 秒  ✅
总处理时间：   83.9 秒  ✅
```

**返回完整数据结构**：
- ✅ `raw_transcript`: 原始语音转文本
- ✅ `cleaned_transcript`: 清洗后的文本
- ✅ `video_info`: 视频元信息
- ✅ `llm_analysis`: AI 分析结果（hook, core, cta）

---

## 技术要点总结

### 1. HTTP 客户端会话管理
- **问题**：复用同一个 httpx 客户端会携带 Cookie/Session 状态
- **解决**：为不同请求创建独立的客户端实例
- **适用场景**：需要避免会话状态影响后续请求的场景

### 2. HTTP Headers 优化
- **发现**：某些服务器（如抖音）会根据 headers 返回不同内容
- **策略**：
  - 移动端 User-Agent：获取完整页面
  - 简化 headers：避免被识别为特定客户端
- **测试方法**：对比不同 headers 组合的响应内容

### 3. Pydantic 可选字段安全访问
- **问题**：直接访问可选字段可能抛出 `AttributeError`
- **解决**：使用 `hasattr()` 或 `getattr()` 进行安全检查
- **最佳实践**：
  ```python
  # 方法 1: hasattr
  if hasattr(obj, 'field') and obj.field is not None:
      use(obj.field)
  
  # 方法 2: getattr with default
  value = getattr(obj, 'field', None)
  if value is not None:
      use(value)
  ```

### 4. 调试技巧

**在容器内测试**：
```bash
docker exec -i container_name python3 <<'PYEOF'
import asyncio
import httpx

async def test():
    # 测试代码
    pass

asyncio.run(test())
PYEOF
```

**对比测试法**：
- 单独测试库函数 ✅
- 对比 API 调用结果 ❌
- 逐步排除变量，定位差异点

---

## 经验教训

### 1. 环境差异不等于网络问题
- ❌ 初步以为是网络限制（需要代理）
- ✅ 实际是 HTTP 客户端实现细节差异

### 2. 服务端行为可能依赖请求细节
- 抖音服务器会根据 headers 返回不同版本的页面
- 简化请求有时比模拟完整浏览器更有效

### 3. 调试工具的重要性
- 快速部署脚本 (`deploy-macmini-quick.sh`) 大大提升调试效率
- 容器内直接测试可以排除很多干扰因素

### 4. 代码演进需要谨慎
- 代码更新前（昨天）可以工作
- 可能是之前的简化逻辑反而更稳定
- 不要盲目增加"完整"的实现

---

## 相关文件

### 修改的文件
- `apps/coprocessor/app/services/url_parser.py` - 抖音解析逻辑
- `apps/coprocessor/app/main.py` - LLM 分析结果处理

### 部署工具
- `deploy-macmini-quick.sh` - Mac mini 快速部署脚本（~30秒）

### 测试 URL
- 测试视频：`https://v.douyin.com/AuPQJ_FVvbQ/`
- Video ID: `7565816808079494440`
- 标题：徕芬 P3 Pro 剃须刀评测

---

## 后续建议

### 1. 监控和告警
考虑添加：
- HTML 内容长度检查（低于 30KB 触发告警）
- `_ROUTER_DATA` 存在性检查
- 失败时记录完整 HTML 内容（便于调试）

### 2. 降级策略
如果简化 headers 失败，可以尝试：
1. 切换不同的 User-Agent
2. 添加 Cookie 模拟
3. 使用浏览器自动化（Playwright/Selenium）

### 3. 文档完善
- 更新 README 故障排除章节
- 记录已知的服务器行为特性
- 维护环境差异对照表

---

## 附录：完整错误日志

<details>
<summary>展开查看原始错误信息</summary>

```
2025-11-05 07:36:28,949 - api.parse - ERROR - [64b2eed8] Service call ShareURLParser.parse failed: 
Failed to parse Douyin video: 从HTML中解析视频信息失败 [Type: URLParserError]

Traceback (most recent call last):
  File "/app/app/services/url_parser.py", line 136, in _parse_douyin
    router_data = self._extract_router_data_optimized(html_content)
  File "/app/app/services/url_parser.py", line 338, in _extract_router_data_optimized
    raise URLParserError("从HTML中解析视频信息失败")
app.services.url_parser.URLParserError: 从HTML中解析视频信息失败
```

</details>

---

**维护者**: Warp AI Agent  
**复核者**: liumingwei  
**最后更新**: 2025-11-05
