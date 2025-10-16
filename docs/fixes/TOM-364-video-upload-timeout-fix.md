# TOM-364: 修复前端视频上传超时问题

## 问题描述

用户通过 https://sp.persimorrow.online 上传视频文件进行分析时，出现前端错误：

```
处理失败
Failed to execute 'text' on 'Response': body stream already read
```

## 根本原因

1. **前端超时问题**：视频处理需要约 66 秒，但前端默认超时时间过短
2. **Response 重复读取问题**：在错误处理代码中，`response.json()` 和 `response.text()` 被依次调用，导致重复读取同一个 Response body stream

## 解决方案

### 1. 延长前端超时时间

在 `src/lib/api-client.ts` 中为所有视频处理请求添加 120 秒超时：

```typescript
// URL mode
response = await fetch(apiUrl, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    url: request.url
  }),
  // Extended timeout for video processing (2 minutes)
  signal: AbortSignal.timeout(120000),
})

// File mode
response = await fetch(apiUrl, {
  method: "POST",
  body: formData,
  // Extended timeout for video processing (2 minutes)
  signal: AbortSignal.timeout(120000),
})
```

### 2. 修复 Response 重复读取问题

使用 `response.clone()` 来避免 "body stream already read" 错误：

```typescript
if (!response.ok) {
  // Clone the response to avoid "body stream already read" error
  const responseClone = response.clone();
  
  // Attempt to parse the JSON error response from the API
  try {
    const errorData: VideoParseResponse = await response.json();
    throw new Error(errorData.message || `API request failed with status ${response.status}`);
  } catch (jsonError) {
    // If the error response isn't JSON, fall back to the raw text from the cloned response
    try {
      const errorText = await responseClone.text();
      throw new Error(`API request failed: ${response.status} ${response.statusText}${errorText ? ` - ${errorText}` : ''}`);
    } catch {
      // If both fail, provide a generic error message
      throw new Error(`API request failed with status ${response.status} ${response.statusText}`);
    }
  }
}
```

### 3. 改进错误提示

添加针对超时和网络错误的用户友好提示：

```typescript
catch (error) {
  // Handle timeout errors specifically
  if (error instanceof Error && error.name === 'TimeoutError') {
    throw new Error('视频处理超时，请尝试上传较小的视频文件或稍后重试');
  }
  
  // Handle network errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    throw new Error('网络连接失败，请检查网络连接后重试');
  }
  
  // Re-throw other errors to be handled by the caller
  throw error
}
```

### 4. 改进用户体验

在 `ProcessingSection` 组件中添加预估处理时间提示：

```typescript
<p className="text-sm text-muted-foreground/80">
  视频处理通常需要 1-2 分钟，请耐心等待
</p>
```

## 修改文件列表

1. `apps/web/src/lib/api-client.ts` - 核心修复
2. `apps/web/src/components/sections/ProcessingSection.tsx` - UX 改进
3. `apps/web/src/lib/__tests__/api-client.test.ts` - 新增测试文件

## 测试验证

### 单元测试

新增了全面的单元测试覆盖：

- ✅ 超时设置验证（URL 和文件模式）
- ✅ 超时错误处理
- ✅ Response 克隆机制测试
- ✅ JSON 和文本错误响应处理
- ✅ 网络错误处理
- ✅ 成功响应解析

运行测试：

```bash
cd apps/web
pnpm test src/lib/__tests__/api-client.test.ts
```

### 手动测试

1. **测试长时间处理**：
   - 上传 30MB+ 的视频文件
   - 验证能够等待 60+ 秒不超时
   - 验证处理成功后能正常显示结果

2. **测试错误处理**：
   - 上传不支持的平台链接
   - 验证错误信息清晰友好
   - 验证不会出现 "body stream already read" 错误

3. **测试超时场景**：
   - 模拟超过 2 分钟的处理
   - 验证显示友好的超时错误提示

## 技术细节

### AbortSignal.timeout() 兼容性

- ✅ Chrome 103+
- ✅ Firefox 100+
- ✅ Safari 16+
- ✅ Edge 103+

如果需要支持更旧的浏览器，可以使用 AbortController 的替代实现。

### Response.clone() 的作用

`Response` 对象的 body 是一个 `ReadableStream`，只能被读取一次。当我们需要多次读取响应体时（如先尝试 JSON，失败后再尝试 text），必须使用 `clone()` 创建副本。

## 验收标准

- ✅ 用户能够成功上传和分析视频文件（30MB+）
- ✅ 前端不会出现 "body stream already read" 错误
- ✅ 长时间处理（60+ 秒）不会导致前端超时
- ✅ 错误处理逻辑完善且用户友好
- ✅ 显示预估处理时间，改善用户体验

## 后续优化建议

1. **实现异步处理模式**（可选）：
   - 提交视频后立即返回任务 ID
   - 前端轮询或使用 WebSocket 获取处理进度
   - 支持离开页面后继续处理

2. **添加进度查询接口**（可选）：
   - 后端提供实时进度更新
   - 显示详细的处理阶段（上传完成、ASR 进行中、LLM 分析中）

3. **文件大小限制提示**：
   - 在上传前显示建议的文件大小范围
   - 对超大文件提前警告预计处理时间

## 参考资料

- [Fetch API - AbortSignal.timeout()](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout)
- [Response.clone()](https://developer.mozilla.org/en-US/docs/Web/API/Response/clone)
- [Linear Issue TOM-364](https://linear.app/tomorrow-persistence/issue/TOM-364)

