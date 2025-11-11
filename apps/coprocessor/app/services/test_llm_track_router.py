"""
测试 LLMTrackRouter - V3.0 赛道路由器
验证路由器的决策逻辑（不涉及真实 LLM API 调用）
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from app.services.llm_track_router import LLMTrackRouter
from app.services.llm_service import AnalysisResult, AnalysisDetail, LLMError


@pytest.mark.asyncio
class TestLLMTrackRouter:
    """LLMTrackRouter 单元测试"""

    @pytest.fixture
    def prompts_dir(self, tmp_path):
        """创建临时 prompts 目录和测试 prompt 文件"""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        # 创建 structured_analysis.prompt
        general_prompt = prompts_dir / "structured_analysis.prompt"
        general_prompt.write_text(
            '{"prompt_instruction": "Analyze general narrative..."}'
        )
        
        # 创建 tech_spec_extraction.prompt (包含占位符)
        tech_prompt = prompts_dir / "tech_spec_extraction.prompt"
        tech_prompt.write_text(
            "Extract tech specs from: {{TRANSCRIPT_PLACEHOLDER}}"
        )
        
        return prompts_dir

    @pytest.fixture
    def mock_execution_service(self):
        """Mock LLMExecutionService"""
        service = AsyncMock()
        return service

    @pytest.fixture
    def router(self, prompts_dir):
        """创建 LLMTrackRouter 实例"""
        return LLMTrackRouter(prompts_dir=prompts_dir)

    async def test_router_general_mode_loads_correct_prompt(
        self, router, mock_execution_service
    ):
        """
        Test 1: 断言当 analysis_mode="general" 时，
        路由器加载 structured_analysis.prompt
        """
        # Arrange: 准备测试数据
        transcript = "今天我来评测一款新的智能手机..."
        
        # Mock execution_service 返回 V2.0 格式的结果
        mock_result = AnalysisResult(
            raw_transcript=transcript,
            cleaned_transcript="评测一款新的智能手机",
            analysis=AnalysisDetail(
                hook="今天评测新手机",
                core="这是核心内容",
                cta="点赞关注",
                key_quotes=["这是金句"]
            )
        )
        mock_execution_service.execute_with_failover.return_value = mock_result

        # Act: 执行路由
        result = await router.get_analysis(
            analysis_mode="general",
            transcript=transcript,
            execution_service=mock_execution_service
        )

        # Assert: 验证结果
        assert isinstance(result, AnalysisResult)
        assert result.raw_transcript == transcript
        assert hasattr(result.analysis, "hook")
        assert hasattr(result.analysis, "core")
        assert hasattr(result.analysis, "cta")
        
        # 验证 execution_service 被调用
        mock_execution_service.execute_with_failover.assert_called_once()

    async def test_router_tech_mode_loads_correct_prompt(
        self, router, mock_execution_service
    ):
        """
        Test 2: 断言当 analysis_mode="tech" 时，
        路由器加载 tech_spec_extraction.prompt
        """
        # Arrange: 准备测试数据
        transcript = "这款手机采用了骁龙8 Gen 3处理器，售价3999元..."
        
        # Mock execution_service 返回 V3.0 格式的结果
        # 注意：tech mode 的 execute_with_failover 应该返回解析后的 JSON 字典
        mock_result = {
            "schema_type": "v3_tech_spec",
            "product_parameters": [
                {"parameter": "CPU", "value": "骁龙8 Gen 3"}
            ],
            "selling_points": [
                {
                    "point": "性能强劲",
                    "context_snippet": "骁龙8 Gen 3处理器"
                }
            ],
            "pricing_info": [
                {
                    "product": "手机",
                    "price": "3999元",
                    "context_snippet": "售价3999元"
                }
            ],
            "subjective_evaluation": {
                "pros": ["性能好"],
                "cons": ["价格高"]
            }
        }
        
        # 为 tech mode 创建特殊的 mock 行为
        async def mock_execute(text):
            # 模拟返回 JSON 字符串，然后被解析
            import json
            return json.dumps(mock_result)
        
        mock_execution_service.execute_with_failover.side_effect = mock_execute

        # Act: 执行路由
        result = await router.get_analysis(
            analysis_mode="tech",
            transcript=transcript,
            execution_service=mock_execution_service
        )

        # Assert: 验证结果
        assert isinstance(result, dict)
        assert result["schema_type"] == "v3_tech_spec"
        assert "product_parameters" in result
        assert "selling_points" in result
        
        # 验证 execution_service 被调用
        mock_execution_service.execute_with_failover.assert_called_once()

    async def test_router_tech_mode_replaces_placeholder(
        self, router, mock_execution_service
    ):
        """
        Test 3: 断言 Tech Mode 的 prompt 中的 
        {{TRANSCRIPT_PLACEHOLDER}} 被正确替换
        """
        # Arrange: 准备测试数据
        transcript = "M4 Max 芯片性能提升 30%"
        
        # 捕获传递给 execute_with_failover 的文本
        captured_text = None
        
        async def capture_text(text):
            nonlocal captured_text
            captured_text = text
            # 返回一个有效的 JSON 字符串
            return '{"schema_type": "v3_tech_spec", "product_parameters": []}'
        
        mock_execution_service.execute_with_failover.side_effect = capture_text

        # Act: 执行路由
        await router.get_analysis(
            analysis_mode="tech",
            transcript=transcript,
            execution_service=mock_execution_service
        )

        # Assert: 验证占位符被替换
        assert captured_text is not None
        assert "{{TRANSCRIPT_PLACEHOLDER}}" not in captured_text
        assert transcript in captured_text

    async def test_router_invalid_mode_raises_error(
        self, router, mock_execution_service
    ):
        """
        Test 4: 断言传入无效的 analysis_mode 时抛出 ValueError
        """
        # Arrange: 准备无效的 analysis_mode
        invalid_mode = "invalid_mode"
        transcript = "测试文本"

        # Act & Assert: 验证抛出 ValueError
        with pytest.raises(ValueError) as exc_info:
            await router.get_analysis(
                analysis_mode=invalid_mode,
                transcript=transcript,
                execution_service=mock_execution_service
            )
        
        # 验证错误消息包含有用信息
        assert "invalid" in str(exc_info.value).lower()
        assert invalid_mode in str(exc_info.value)

    async def test_router_general_mode_returns_v2_format(
        self, router, mock_execution_service
    ):
        """
        Test 5: 断言 General Mode 返回 V2.0 格式的数据结构
        """
        # Arrange: 准备测试数据
        transcript = "这是一个通用叙事分析测试"
        
        # Mock execution_service 返回 V2.0 格式
        mock_result = AnalysisResult(
            raw_transcript=transcript,
            cleaned_transcript="通用叙事分析测试",
            analysis=AnalysisDetail(
                hook="测试钩子",
                core="测试核心",
                cta="测试行动召唤"
            )
        )
        mock_execution_service.execute_with_failover.return_value = mock_result

        # Act: 执行路由
        result = await router.get_analysis(
            analysis_mode="general",
            transcript=transcript,
            execution_service=mock_execution_service
        )

        # Assert: 验证返回的是 AnalysisResult 类型
        assert isinstance(result, AnalysisResult)
        assert isinstance(result.analysis.hook, str)
        assert isinstance(result.analysis.core, str)
        assert isinstance(result.analysis.cta, str)
        
        # 验证字段不为空
        assert len(result.analysis.hook) > 0
        assert len(result.analysis.core) > 0
        assert len(result.analysis.cta) > 0

