# LLM服务适配器模式需求文档

## 介绍

本文档定义了LLM服务适配器模式的需求，该模式支持DeepSeek和Kimi两种LLM服务，具备主备切换功能，并实现Prompt与代码的分离。

## 需求

### 需求1：LLM服务适配器架构

**用户故事：** 作为开发者，我希望有一个统一的LLM服务接口，以便可以轻松切换不同的LLM提供商。

#### 验收标准

1. WHEN 系统初始化时 THEN 系统应该提供一个LLMService协议接口
2. WHEN 创建DeepSeek适配器时 THEN 适配器应该实现LLMService协议
3. WHEN 创建Kimi适配器时 THEN 适配器应该实现LLMService协议
4. WHEN 调用任何适配器的analyze方法时 THEN 应该返回标准化的AnalysisResult对象

### 需求2：外部Prompt配置

**用户故事：** 作为开发者，我希望系统提示词存储在外部文件中，以便可以独立于代码进行修改和版本控制。

#### 验收标准

1. WHEN 系统启动时 THEN 应该从`app/prompts/structured_analysis.prompt`文件加载系统提示词
2. WHEN 适配器初始化时 THEN 应该读取外部prompt文件而不是使用硬编码的提示词
3. IF prompt文件不存在 THEN 系统应该抛出适当的错误
4. WHEN prompt文件内容更新时 THEN 重启服务后应该使用新的prompt内容

### 需求3：主备切换机制

**用户故事：** 作为系统管理员，我希望LLM服务具备故障切换能力，以确保服务的高可用性。

#### 验收标准

1. WHEN 主LLM服务正常工作时 THEN 系统应该使用主服务并且不调用备用服务
2. WHEN 主LLM服务失败时 THEN 系统应该自动切换到备用服务
3. WHEN 主服务和备用服务都失败时 THEN 系统应该抛出LLMError异常
4. WHEN 故障切换发生时 THEN 系统应该返回来自备用服务的结果

### 需求4：环境变量配置

**用户故事：** 作为部署工程师，我希望通过环境变量配置LLM服务的API密钥和基础URL。

#### 验收标准

1. WHEN DeepSeek适配器初始化时 THEN 应该从DEEPSEEK_API_KEY环境变量读取API密钥
2. WHEN Kimi适配器初始化时 THEN 应该从KIMI_API_KEY环境变量读取API密钥
3. IF 必需的环境变量未设置 THEN 系统应该抛出ValueError异常
4. WHEN 设置了自定义基础URL环境变量时 THEN 适配器应该使用自定义URL

### 需求5：结构化分析结果

**用户故事：** 作为API用户，我希望LLM分析返回结构化的结果，包含hook、core和cta三个部分。

#### 验收标准

1. WHEN LLM分析完成时 THEN 应该返回包含hook、core、cta字段的AnalysisResult对象
2. WHEN LLM返回无效JSON时 THEN 系统应该抛出LLMError异常
3. WHEN LLM返回的JSON缺少必需字段时 THEN 系统应该抛出LLMError异常
4. WHEN 分析成功时 THEN 结果应该符合预定义的数据模型

### 需求6：错误处理和重试

**用户故事：** 作为系统用户，我希望系统能够优雅地处理各种错误情况，并提供有意义的错误信息。

#### 验收标准

1. WHEN HTTP请求失败时 THEN 系统应该抛出包含详细错误信息的LLMError
2. WHEN 网络连接超时时 THEN 系统应该抛出LLMError并包含超时信息
3. WHEN API返回错误状态码时 THEN 系统应该抛出相应的LLMError
4. WHEN 发生未预期的异常时 THEN 系统应该将其包装为LLMError并保留原始异常信息

### 需求7：工厂函数支持

**用户故事：** 作为开发者，我希望有一个便捷的工厂函数来创建配置好的LLM路由器实例。

#### 验收标准

1. WHEN 调用create_llm_router_from_env函数时 THEN 应该返回配置好的LLMRouter实例
2. WHEN 环境变量正确设置时 THEN 工厂函数应该创建DeepSeek作为主服务，Kimi作为备用服务
3. IF 必需的环境变量未设置 THEN 工厂函数应该抛出ValueError异常
4. WHEN 工厂函数成功执行时 THEN 返回的路由器应该可以立即使用