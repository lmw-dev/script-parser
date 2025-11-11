"""
V1.0 LLM 执行服务 (Execution Service)
职责: 可靠地执行 LLM 请求，包含主备切换逻辑

此模块实现了 V1.0 的故障切换 (Failover) 可靠性设计。
它接收主 LLM 服务和备用 LLM 服务，在主服务失败时自动切换到备用服务。
"""

from typing import Protocol

from .llm_service import AnalysisResult, LLMError


class LLMService(Protocol):
    """LLM 服务协议（用于类型提示）"""

    async def analyze(self, text: str) -> AnalysisResult:
        """分析文本并返回结构化结果"""
        ...


class LLMExecutionService:
    """
    V1.0 LLM 执行服务 - 执行层（包含主备切换）

    此服务封装了 LLM 调用的可靠性逻辑：
    1. 优先使用主服务 (Primary)
    2. 主服务失败时，自动切换到备用服务 (Fallback)
    3. 所有服务都失败时，抛出包含详细错误信息的异常

    Attributes:
        primary: 主 LLM 服务适配器（例如 DeepSeekAdapter）
        fallback: 备用 LLM 服务适配器（例如 KimiAdapter）

    Example:
        >>> execution_service = LLMExecutionService(
        ...     primary=DeepSeekAdapter(),
        ...     fallback=KimiAdapter()
        ... )
        >>> result = await execution_service.execute_with_failover("分析这段文本...")
    """

    def __init__(self, primary: LLMService, fallback: LLMService):
        """
        初始化 LLM 执行服务

        Args:
            primary: 主 LLM 服务（优先调用）
            fallback: 备用 LLM 服务（主服务失败时调用）
        """
        self.primary = primary
        self.fallback = fallback

    async def execute_with_failover(self, text: str) -> AnalysisResult:
        """
        执行 LLM 分析，支持主备切换

        此方法实现了可靠的故障切换逻辑：
        1. 首先尝试主服务 (primary)
        2. 如果主服务抛出 LLMError，捕获错误并尝试备用服务 (fallback)
        3. 如果备用服务也失败，抛出包含两个服务错误信息的 LLMError

        Args:
            text: 要分析的文本内容

        Returns:
            AnalysisResult: 分析结果对象，包含 raw_transcript、cleaned_transcript 和 analysis

        Raises:
            LLMError: 当所有 LLM 服务都失败时，抛出包含详细错误信息的异常

        Example:
            >>> try:
            ...     result = await service.execute_with_failover("测试文本")
            ...     print(result.analysis.hook)
            ... except LLMError as e:
            ...     print(f"所有服务都失败: {e}")
        """
        primary_error = None
        fallback_error = None

        # 第一步：尝试主服务
        try:
            return await self.primary.analyze(text)
        except LLMError as e:
            primary_error = str(e)
            # 记录主服务失败日志（用于调试）
            print(f"[LLMExecutionService] Primary service failed: {primary_error}")

            # 第二步：主服务失败，尝试备用服务
            try:
                return await self.fallback.analyze(text)
            except LLMError as e:
                fallback_error = str(e)
                # 记录备用服务失败日志（用于调试）
                print(f"[LLMExecutionService] Fallback service failed: {fallback_error}")

                # 第三步：所有服务都失败，抛出详细错误
                raise LLMError(
                    f"All LLM services failed.\n"
                    f"Primary (DeepSeek) error: {primary_error}\n"
                    f"Fallback (Kimi) error: {fallback_error}"
                ) from e

