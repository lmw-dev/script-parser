"""
V3.0 LLM 赛道路由器 (Track Router)
职责: 根据 analysis_mode 决策使用哪个 prompt 和 schema

此模块实现了 V3.0 的"赛道路由"功能，它是"决策层"，负责根据用户选择的
分析模式（通用叙事 vs 科技评测）来选择合适的 prompt 模板和输出 schema。

路由映射:
- "general" -> structured_analysis.prompt (V2.0 叙事分析)
- "tech"    -> tech_spec_extraction.prompt (V3.0 科技规格提取)
"""

import json
from pathlib import Path
from typing import Any

from .llm_execution_service import LLMExecutionService
from .llm_service import AnalysisResult, LLMError


class LLMTrackRouter:
    """
    V3.0 赛道路由器 - 决策层

    此路由器负责根据 analysis_mode 参数，决定使用哪个 prompt 模板和哪个输出 schema。
    它不直接调用 LLM API，而是将决策结果传递给 LLMExecutionService 执行。

    Attributes:
        prompts_dir: Prompt 文件所在目录路径
        route_map: 路由映射表，定义每个模式对应的 prompt 文件和输出类型

    Example:
        >>> router = LLMTrackRouter(prompts_dir=Path("app/prompts"))
        >>> execution_service = LLMExecutionService(primary=DeepSeek(), fallback=Kimi())
        >>> result = await router.get_analysis(
        ...     analysis_mode="tech",
        ...     transcript="M4 Max 芯片性能提升30%",
        ...     execution_service=execution_service
        ... )
    """

    def __init__(self, prompts_dir: Path):
        """
        初始化 LLM 赛道路由器

        Args:
            prompts_dir: Prompt 文件所在目录的路径对象
        """
        self.prompts_dir = prompts_dir

        # 路由映射表：定义每个分析模式对应的配置
        self.route_map = {
            "general": {
                "prompt_file": "structured_analysis.prompt",
                "output_type": "v2_narrative"
            },
            "tech": {
                "prompt_file": "tech_spec_extraction.prompt",
                "output_type": "v3_tech_spec"
            }
        }

    async def get_analysis(
        self,
        analysis_mode: str,
        transcript: str,
        execution_service: LLMExecutionService
    ) -> AnalysisResult | dict[str, Any]:
        """
        根据 analysis_mode 路由到对应的分析流程

        此方法是路由器的核心逻辑：
        1. 验证 analysis_mode 是否有效
        2. 根据 analysis_mode 加载对应的 prompt 模板
        3. 对于 tech mode，替换 prompt 中的占位符
        4. 调用 execution_service 执行分析
        5. 对于 tech mode，解析返回的 JSON 字符串

        Args:
            analysis_mode: 分析模式，必须是 "general" 或 "tech"
            transcript: 原始转录文本
            execution_service: LLM 执行服务实例，用于实际执行分析

        Returns:
            - 如果是 general mode: 返回 AnalysisResult 对象（V2.0 格式）
            - 如果是 tech mode: 返回 dict（V3.0 格式）

        Raises:
            ValueError: 当 analysis_mode 无效时
            LLMError: 当分析失败时（由 execution_service 抛出）
            FileNotFoundError: 当 prompt 文件不存在时

        Example:
            >>> # General Mode
            >>> result = await router.get_analysis("general", "今天评测...", service)
            >>> print(result.analysis.hook)  # AnalysisResult 对象

            >>> # Tech Mode
            >>> result = await router.get_analysis("tech", "M4 Max...", service)
            >>> print(result["product_parameters"])  # Dict 对象
        """
        # 第一步：验证 analysis_mode
        if analysis_mode not in self.route_map:
            valid_modes = ", ".join(self.route_map.keys())
            raise ValueError(
                f"Invalid analysis_mode: '{analysis_mode}'. "
                f"Must be one of: {valid_modes}"
            )

        # 第二步：获取路由配置
        route_config = self.route_map[analysis_mode]
        prompt_file = route_config["prompt_file"]
        # output_type = route_config["output_type"]  # 暂时未使用，保留用于未来扩展

        # 第三步：加载 prompt 模板
        prompt_content = self._load_prompt(prompt_file)

        # 第四步：根据模式处理 prompt 和执行分析
        if analysis_mode == "general":
            # General Mode: 直接使用 transcript 调用 execution_service
            # execution_service 会使用 DeepSeek/Kimi 的系统提示词（在 llm_service.py 中加载）
            result = await execution_service.execute_with_failover(transcript)
            return result

        elif analysis_mode == "tech":
            # Tech Mode: 需要替换 prompt 中的占位符
            prompt_with_transcript = prompt_content.replace(
                "{{TRANSCRIPT_PLACEHOLDER}}", transcript
            )

            # 调用 execution_service（传入完整的 prompt）
            # 注意：tech mode 的 prompt 是完整的指令，不依赖 Adapter 的系统提示词
            # 返回值应该是 JSON 字符串
            raw_response = await execution_service.execute_with_failover(
                prompt_with_transcript
            )

            # Tech mode 的 execution_service 会返回一个 AnalysisResult
            # 但我们需要从中提取 JSON 字符串并解析
            # 这里假设 LLM 返回的是包含 tech spec 的 JSON
            # 我们需要解析 raw_response.analysis 字段或整个响应

            # 如果返回的是 AnalysisResult，我们尝试从 cleaned_transcript 或其他字段提取 JSON
            if isinstance(raw_response, AnalysisResult):
                # 尝试从 analysis.core 或 cleaned_transcript 解析 JSON
                json_text = raw_response.cleaned_transcript or raw_response.raw_transcript
                try:
                    tech_spec_data = json.loads(json_text)
                    return tech_spec_data
                except json.JSONDecodeError as e:
                    # 如果解析失败，尝试从 analysis 字段构造字典
                    # 这是一个兼容性处理
                    raise LLMError(
                        f"Failed to parse tech spec JSON from LLM response. "
                        f"Response preview: {json_text[:200]}"
                    ) from e
            else:
                # 如果直接返回字符串，尝试解析
                try:
                    tech_spec_data = json.loads(raw_response)
                    return tech_spec_data
                except json.JSONDecodeError as e:
                    raise LLMError(
                        f"Failed to parse tech spec JSON: {str(e)}. "
                        f"Response preview: {str(raw_response)[:200]}"
                    ) from e

        # 不应该到达这里
        raise ValueError(f"Unexpected analysis_mode: {analysis_mode}")

    def _load_prompt(self, file_name: str) -> str:
        """
        从文件加载 prompt 模板

        此方法负责从 prompts_dir 目录中读取指定的 prompt 文件。

        Args:
            file_name: Prompt 文件名（例如 "structured_analysis.prompt"）

        Returns:
            str: Prompt 文件的内容

        Raises:
            FileNotFoundError: 当指定的文件不存在时

        Example:
            >>> content = router._load_prompt("structured_analysis.prompt")
            >>> print(content[:50])
        """
        prompt_path = self.prompts_dir / file_name

        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_path}. "
                f"Please ensure the file exists in {self.prompts_dir}"
            )

        with open(prompt_path, encoding="utf-8") as f:
            content = f.read()

        return content

