"""
测试 LLMExecutionService - V1.0 LLM 执行服务
验证主备切换逻辑的可靠性
"""

import pytest
from unittest.mock import AsyncMock, Mock
from app.services.llm_execution_service import LLMExecutionService
from app.services.llm_service import AnalysisResult, AnalysisDetail, LLMError


@pytest.mark.asyncio
class TestLLMExecutionService:
    """LLMExecutionService 单元测试"""

    @pytest.fixture
    def mock_primary_service(self):
        """Mock 主 LLM 服务 (DeepSeek)"""
        service = AsyncMock()
        service.name = "DeepSeek"  # 用于日志和调试
        return service

    @pytest.fixture
    def mock_fallback_service(self):
        """Mock 备用 LLM 服务 (Kimi)"""
        service = AsyncMock()
        service.name = "Kimi"
        return service

    @pytest.fixture
    def execution_service(self, mock_primary_service, mock_fallback_service):
        """创建 LLMExecutionService 实例"""
        return LLMExecutionService(
            primary=mock_primary_service,
            fallback=mock_fallback_service
        )

    async def test_execution_service_primary_success(
        self, execution_service, mock_primary_service, mock_fallback_service
    ):
        """
        Test 1: 断言当主服务 (DeepSeek) 成功时，
        直接返回结果，不调用备用服务
        """
        # Arrange: 准备测试数据
        test_text = "测试文本用于分析"
        
        # Mock 主服务返回成功结果
        expected_result = AnalysisResult(
            raw_transcript=test_text,
            cleaned_transcript="测试文本用于分析",
            analysis=AnalysisDetail(
                hook="测试钩子",
                core="测试核心内容",
                cta="测试行动召唤"
            )
        )
        mock_primary_service.analyze.return_value = expected_result

        # Act: 执行分析
        result = await execution_service.execute_with_failover(test_text)

        # Assert: 验证主服务被调用，备用服务未被调用
        mock_primary_service.analyze.assert_called_once_with(test_text)
        mock_fallback_service.analyze.assert_not_called()
        
        # 验证返回的结果是主服务的结果
        assert result == expected_result
        assert result.raw_transcript == test_text

    async def test_execution_service_primary_fails_fallback_succeeds(
        self, execution_service, mock_primary_service, mock_fallback_service
    ):
        """
        Test 2: 断言当主服务失败时，自动切换到备用服务
        """
        # Arrange: 准备测试数据
        test_text = "测试主备切换场景"
        
        # Mock 主服务抛出 LLMError
        primary_error = LLMError("DeepSeek API timeout: Request took too long")
        mock_primary_service.analyze.side_effect = primary_error
        
        # Mock 备用服务返回成功结果
        fallback_result = AnalysisResult(
            raw_transcript=test_text,
            cleaned_transcript="测试主备切换场景",
            analysis=AnalysisDetail(
                hook="备用服务钩子",
                core="备用服务核心内容",
                cta="备用服务行动召唤"
            )
        )
        mock_fallback_service.analyze.return_value = fallback_result

        # Act: 执行分析
        result = await execution_service.execute_with_failover(test_text)

        # Assert: 验证主服务和备用服务都被调用
        mock_primary_service.analyze.assert_called_once_with(test_text)
        mock_fallback_service.analyze.assert_called_once_with(test_text)
        
        # 验证返回的是备用服务的结果
        assert result == fallback_result
        assert result.analysis.hook == "备用服务钩子"

    async def test_execution_service_all_fail(
        self, execution_service, mock_primary_service, mock_fallback_service
    ):
        """
        Test 3: 断言当所有服务都失败时，
        抛出包含详细错误信息的 LLMError
        """
        # Arrange: 准备测试数据
        test_text = "测试所有服务都失败的场景"
        
        # Mock 主服务抛出错误
        primary_error_msg = "DeepSeek API error: Connection timeout"
        mock_primary_service.analyze.side_effect = LLMError(primary_error_msg)
        
        # Mock 备用服务也抛出错误
        fallback_error_msg = "Kimi API error: Rate limit exceeded"
        mock_fallback_service.analyze.side_effect = LLMError(fallback_error_msg)

        # Act & Assert: 验证抛出 LLMError
        with pytest.raises(LLMError) as exc_info:
            await execution_service.execute_with_failover(test_text)
        
        # 验证错误消息同时包含主服务和备用服务的错误信息
        error_message = str(exc_info.value)
        assert "DeepSeek" in error_message or primary_error_msg in error_message
        assert "Kimi" in error_message or fallback_error_msg in error_message
        
        # 验证两个服务都被调用
        mock_primary_service.analyze.assert_called_once_with(test_text)
        mock_fallback_service.analyze.assert_called_once_with(test_text)

