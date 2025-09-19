"""
LLM服务适配器模式实现
支持DeepSeek和Kimi，具备主备切换功能
"""

import json
import os
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from ..config import TimeoutConfig
from ..http_client import get_http_client

# Prompt文件路径
PROMPT_FILE_PATH = (
    Path(__file__).parent.parent / "prompts" / "structured_analysis.prompt"
)


class LLMError(Exception):
    """LLM服务异常"""

    pass


class AnalysisResult(BaseModel):
    """分析结果数据模型"""

    hook: str
    core: str
    cta: str


class LLMService(Protocol):
    """LLM服务协议"""

    async def analyze(self, text: str) -> AnalysisResult:
        """分析文本并返回结构化结果"""
        ...


class DeepSeekAdapter:
    """DeepSeek适配器"""

    def __init__(self, api_key: str = None):
        """
        初始化DeepSeek适配器

        Args:
            api_key: API密钥，如果为None则从环境变量获取

        Raises:
            ValueError: 当API密钥未设置时
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set.")

        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

        # 从文件加载系统提示词
        with open(PROMPT_FILE_PATH, encoding="utf-8") as f:
            self.system_prompt = f.read()

    async def analyze(self, text: str) -> AnalysisResult:
        """
        使用DeepSeek分析文本

        Args:
            text: 要分析的文本

        Returns:
            分析结果

        Raises:
            LLMError: 当分析失败时
        """
        try:
            client = await get_http_client()
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": text},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
                timeout=TimeoutConfig.LLM_TIMEOUT,
            )

            response.raise_for_status()
            result = response.json()

            # 提取响应内容
            content = result["choices"][0]["message"]["content"]

            # 解析JSON响应
            try:
                analysis_data = json.loads(content)
                return AnalysisResult(
                    hook=analysis_data["hook"],
                    core=analysis_data["core"],
                    cta=analysis_data["cta"],
                )
            except (json.JSONDecodeError, KeyError) as e:
                raise LLMError(f"Failed to parse DeepSeek response: {str(e)}") from e

        except Exception as e:
            if isinstance(e, LLMError):
                raise
            raise LLMError(f"DeepSeek API error: {str(e)}") from e


class KimiAdapter:
    """Kimi适配器"""

    def __init__(self, api_key: str = None):
        """
        初始化Kimi适配器

        Args:
            api_key: API密钥，如果为None则从环境变量获取

        Raises:
            ValueError: 当API密钥未设置时
        """
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        if not self.api_key:
            raise ValueError("KIMI_API_KEY environment variable not set.")

        self.base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn")

        # 从文件加载系统提示词
        with open(PROMPT_FILE_PATH, encoding="utf-8") as f:
            self.system_prompt = f.read()

    async def analyze(self, text: str) -> AnalysisResult:
        """
        使用Kimi分析文本

        Args:
            text: 要分析的文本

        Returns:
            分析结果

        Raises:
            LLMError: 当分析失败时
        """
        try:
            client = await get_http_client()
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "moonshot-v1-8k",
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": text},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
                timeout=TimeoutConfig.LLM_TIMEOUT,
            )

            response.raise_for_status()
            result = response.json()

            # 提取响应内容
            content = result["choices"][0]["message"]["content"]

            # 解析JSON响应
            try:
                analysis_data = json.loads(content)
                return AnalysisResult(
                    hook=analysis_data["hook"],
                    core=analysis_data["core"],
                    cta=analysis_data["cta"],
                )
            except (json.JSONDecodeError, KeyError) as e:
                raise LLMError(f"Failed to parse Kimi response: {str(e)}") from e

        except Exception as e:
            if isinstance(e, LLMError):
                raise
            raise LLMError(f"Kimi API error: {str(e)}") from e


class LLMRouter:
    """LLM路由器，实现主备切换"""

    def __init__(self, primary: LLMService, fallback: LLMService):
        """
        初始化LLM路由器

        Args:
            primary: 主LLM服务
            fallback: 备用LLM服务
        """
        self.primary = primary
        self.fallback = fallback

    async def analyze(self, text: str) -> AnalysisResult:
        """
        分析文本，支持主备切换

        Args:
            text: 要分析的文本

        Returns:
            分析结果

        Raises:
            LLMError: 当所有服务都失败时
        """
        # 尝试主服务
        try:
            return await self.primary.analyze(text)
        except LLMError:
            # 主服务失败，尝试备用服务
            try:
                return await self.fallback.analyze(text)
            except LLMError:
                # 所有服务都失败
                raise LLMError(
                    "All LLM services failed. Both primary and fallback services are unavailable."
                ) from None


def create_llm_router_from_env() -> LLMRouter:
    """
    从环境变量创建LLM路由器

    Returns:
        配置好的LLM路由器实例

    Raises:
        ValueError: 当必需的环境变量未设置时
    """
    # 创建DeepSeek适配器作为主服务
    primary = DeepSeekAdapter()

    # 创建Kimi适配器作为备用服务
    fallback = KimiAdapter()

    return LLMRouter(primary=primary, fallback=fallback)
