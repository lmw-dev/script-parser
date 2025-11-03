"""
LLM Service Tests
测试LLM服务适配器模式和故障切换功能
"""

from unittest.mock import AsyncMock, Mock, mock_open, patch

import pytest

from .llm_service import (
    AnalysisDetail,
    AnalysisResult,
    DeepSeekAdapter,
    KimiAdapter,
    LLMError,
    LLMRouter,
    LLMService,
)


class TestLLMService:
    """LLM Service 协议测试"""

    def test_llm_service_protocol_exists(self):
        """测试LLMService协议是否存在"""
        # 这个测试确保LLMService协议被正确定义
        assert hasattr(LLMService, "analyze")


class TestAnalysisResult:
    """AnalysisResult 数据模型测试"""

    def test_analysis_result_creation(self):
        """测试AnalysisResult创建 (V2.2)"""
        analysis_detail = AnalysisDetail(
            hook="This is a hook",
            core="This is the core content",
            cta="Please like and subscribe",
        )
        result = AnalysisResult(
            raw_transcript="Raw transcript text",
            cleaned_transcript="Cleaned transcript text",
            analysis=analysis_detail,
        )

        assert result.raw_transcript == "Raw transcript text"
        assert result.cleaned_transcript == "Cleaned transcript text"
        assert result.analysis.hook == "This is a hook"
        assert result.analysis.core == "This is the core content"
        assert result.analysis.cta == "Please like and subscribe"

    def test_analysis_result_validation(self):
        """测试AnalysisResult验证"""
        # 测试必需字段
        with pytest.raises(ValueError):
            AnalysisResult()  # 缺少必需字段


class TestDeepSeekAdapter:
    """DeepSeek适配器测试"""

    @patch("builtins.open", new_callable=mock_open, read_data="Test system prompt")
    def test_deepseek_adapter_initialization(self, mock_file):
        """测试DeepSeek适配器初始化和prompt加载"""
        adapter = DeepSeekAdapter(api_key="test-key")

        assert adapter.api_key == "test-key"
        assert adapter.system_prompt == "Test system prompt"

        # 验证文件被正确读取
        mock_file.assert_called_once()
        call_args = mock_file.call_args[0]
        assert "structured_analysis.prompt" in str(call_args[0])

    @patch("builtins.open", new_callable=mock_open, read_data="Test system prompt")
    def test_deepseek_adapter_env_api_key(self, mock_file):
        """测试从环境变量读取API密钥"""
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "env-key"}):
            adapter = DeepSeekAdapter()
            assert adapter.api_key == "env-key"

    @patch("builtins.open", new_callable=mock_open, read_data="Test system prompt")
    def test_deepseek_adapter_missing_api_key(self, mock_file):
        """测试缺少API密钥时抛出异常"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
                DeepSeekAdapter()

    @pytest.mark.asyncio
    @patch("builtins.open", new_callable=mock_open, read_data="Test system prompt")
    @patch("httpx.AsyncClient")
    async def test_deepseek_adapter_analyze_success(self, mock_httpx_client, mock_file):
        """测试DeepSeek适配器成功分析 (V2.2)"""
        # Mock HTTP响应 (V2.2 结构)
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"raw_transcript": "Raw text", "cleaned_transcript": "Cleaned text", "analysis": {"hook": "Test hook", "core": "Test core", "cta": "Test CTA"}}'
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance

        # 测试分析
        adapter = DeepSeekAdapter(api_key="test-key")
        result = await adapter.analyze("Test transcript")

        # 验证结果 (V2.2)
        assert isinstance(result, AnalysisResult)
        assert result.raw_transcript == "Raw text"
        assert result.cleaned_transcript == "Cleaned text"
        assert result.analysis.hook == "Test hook"
        assert result.analysis.core == "Test core"
        assert result.analysis.cta == "Test CTA"

        # 验证HTTP调用
        mock_client_instance.post.assert_called_once()
        call_args = mock_client_instance.post.call_args

        # 验证URL (第一个位置参数)
        assert "deepseek" in call_args[0][0]

        # 验证请求体包含系统提示词
        request_data = call_args[1]["json"]
        assert any(
            "Test system prompt" in str(msg.get("content", ""))
            for msg in request_data.get("messages", [])
        )

    @pytest.mark.asyncio
    @patch("builtins.open", new_callable=mock_open, read_data="Test system prompt")
    @patch("httpx.AsyncClient")
    async def test_deepseek_adapter_analyze_http_error(
        self, mock_httpx_client, mock_file
    ):
        """测试DeepSeek适配器HTTP错误处理"""
        # Mock HTTP错误
        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = Exception("HTTP Error")
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance

        adapter = DeepSeekAdapter(api_key="test-key")

        with pytest.raises(LLMError, match="DeepSeek API error"):
            await adapter.analyze("Test transcript")

    @pytest.mark.asyncio
    @patch("builtins.open", new_callable=mock_open, read_data="Test system prompt")
    @patch("httpx.AsyncClient")
    async def test_deepseek_adapter_analyze_json_parse_error(
        self, mock_httpx_client, mock_file
    ):
        """测试DeepSeek适配器JSON解析错误"""
        # Mock无效JSON响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Invalid JSON content"}}]
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance

        adapter = DeepSeekAdapter(api_key="test-key")

        with pytest.raises(LLMError, match="Failed to parse"):
            await adapter.analyze("Test transcript")


class TestKimiAdapter:
    """Kimi适配器测试"""

    @patch("builtins.open", new_callable=mock_open, read_data="Test system prompt")
    def test_kimi_adapter_initialization(self, mock_file):
        """测试Kimi适配器初始化"""
        adapter = KimiAdapter(api_key="test-key")

        assert adapter.api_key == "test-key"
        assert adapter.system_prompt == "Test system prompt"

    @patch("builtins.open", new_callable=mock_open, read_data="Test system prompt")
    def test_kimi_adapter_env_api_key(self, mock_file):
        """测试从环境变量读取API密钥"""
        with patch.dict("os.environ", {"KIMI_API_KEY": "env-key"}):
            adapter = KimiAdapter()
            assert adapter.api_key == "env-key"

    @pytest.mark.asyncio
    @patch("builtins.open", new_callable=mock_open, read_data="Test system prompt")
    @patch("httpx.AsyncClient")
    async def test_kimi_adapter_analyze_success(self, mock_httpx_client, mock_file):
        """测试Kimi适配器成功分析"""
        # Mock HTTP响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"raw_transcript": "Raw text", "cleaned_transcript": "Cleaned text", "analysis": {"hook": "Kimi hook", "core": "Kimi core", "cta": "Kimi CTA"}}'
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance

        # 测试分析
        adapter = KimiAdapter(api_key="test-key")
        result = await adapter.analyze("Test transcript")

        # 验证结果 (V2.2)
        assert isinstance(result, AnalysisResult)
        assert result.raw_transcript == "Raw text"
        assert result.cleaned_transcript == "Cleaned text"
        assert result.analysis.hook == "Kimi hook"
        assert result.analysis.core == "Kimi core"
        assert result.analysis.cta == "Kimi CTA"

        # 验证HTTP调用
        mock_client_instance.post.assert_called_once()
        call_args = mock_client_instance.post.call_args

        # 验证URL (第一个位置参数)
        assert "moonshot" in call_args[0][0]


class TestLLMRouter:
    """LLM路由器测试"""

    def test_llm_router_initialization(self):
        """测试LLM路由器初始化"""
        primary = Mock(spec=LLMService)
        fallback = Mock(spec=LLMService)

        router = LLMRouter(primary=primary, fallback=fallback)

        assert router.primary is primary
        assert router.fallback is fallback

    @pytest.mark.asyncio
    async def test_llm_router_primary_success(self):
        """测试主服务成功场景 (V2.2)"""
        # Mock主服务成功
        primary = AsyncMock(spec=LLMService)
        expected_result = AnalysisResult(
            raw_transcript="Raw text",
            cleaned_transcript="Cleaned text",
            analysis=AnalysisDetail(
                hook="Primary hook", core="Primary core", cta="Primary CTA"
            ),
        )
        primary.analyze.return_value = expected_result

        # Mock备用服务（不应被调用）
        fallback = AsyncMock(spec=LLMService)

        router = LLMRouter(primary=primary, fallback=fallback)
        result = await router.analyze("Test transcript")

        # 验证结果来自主服务
        assert result == expected_result

        # 验证调用
        primary.analyze.assert_called_once_with("Test transcript")
        fallback.analyze.assert_not_called()

    @pytest.mark.asyncio
    async def test_llm_router_failover_success(self):
        """测试故障切换成功场景 (V2.2)"""
        # Mock主服务失败
        primary = AsyncMock(spec=LLMService)
        primary.analyze.side_effect = LLMError("Primary service failed")

        # Mock备用服务成功
        fallback = AsyncMock(spec=LLMService)
        expected_result = AnalysisResult(
            raw_transcript="Raw text",
            cleaned_transcript="Cleaned text",
            analysis=AnalysisDetail(
                hook="Fallback hook", core="Fallback core", cta="Fallback CTA"
            ),
        )
        fallback.analyze.return_value = expected_result

        router = LLMRouter(primary=primary, fallback=fallback)
        result = await router.analyze("Test transcript")

        # 验证结果来自备用服务
        assert result == expected_result

        # 验证调用
        primary.analyze.assert_called_once_with("Test transcript")
        fallback.analyze.assert_called_once_with("Test transcript")

    @pytest.mark.asyncio
    async def test_llm_router_all_services_fail(self):
        """测试所有服务都失败的场景"""
        # Mock主服务失败
        primary = AsyncMock(spec=LLMService)
        primary.analyze.side_effect = LLMError("Primary service failed")

        # Mock备用服务也失败
        fallback = AsyncMock(spec=LLMService)
        fallback.analyze.side_effect = LLMError("Fallback service failed")

        router = LLMRouter(primary=primary, fallback=fallback)

        # 验证抛出异常
        with pytest.raises(LLMError, match="All LLM services failed"):
            await router.analyze("Test transcript")

        # 验证两个服务都被调用
        primary.analyze.assert_called_once_with("Test transcript")
        fallback.analyze.assert_called_once_with("Test transcript")


class TestLLMError:
    """LLM错误异常测试"""

    def test_llm_error_creation(self):
        """测试LLMError异常创建"""
        error = LLMError("Test error message")
        assert str(error) == "Test error message"

    def test_llm_error_inheritance(self):
        """测试LLMError异常继承关系"""
        error = LLMError("Test error")
        assert isinstance(error, Exception)
