"""
LLM服务适配器模式实现
支持Kimi和DeepSeek，具备主备切换功能（默认使用Kimi作为主服务）
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


class AnalysisDetail(BaseModel):
    """分析详情数据模型 - V3.0 支持 key_quotes"""

    hook: str
    core: str
    cta: str
    key_quotes: list[str] | None = None  # V3.0: 金句提炼


class AnalysisResult(BaseModel):
    """V3.0 分析结果数据模型 - 包含原始稿、清洗稿和分析结果（含 key_quotes）"""

    raw_transcript: str
    cleaned_transcript: str
    analysis: AnalysisDetail


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
                    "max_tokens": 4000,
                },
                timeout=TimeoutConfig.LLM_TIMEOUT,
            )

            response.raise_for_status()
            result = response.json()

            # 提取响应内容
            content = result["choices"][0]["message"]["content"]
            print(f"[DEBUG] DeepSeek API response received, content length: {len(content)}")

            # 解析JSON响应 (支持 V2.2 格式)
            try:
                # 移除可能的 markdown 代码块标记
                cleaned_content = content.strip()
                if cleaned_content.startswith("```json"):
                    cleaned_content = cleaned_content[7:]
                elif cleaned_content.startswith("```"):
                    cleaned_content = cleaned_content[3:]
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]
                cleaned_content = cleaned_content.strip()

                analysis_data = json.loads(cleaned_content)

                # V3.0: 检查是否为科技评测响应格式
                if "schema_type" in analysis_data and analysis_data["schema_type"] == "v3_tech_spec":
                    # V3.0 科技评测模式：直接返回 JSON 字符串供路由器解析
                    # 将 JSON 对象转为字符串存储在 cleaned_transcript 中
                    return AnalysisResult(
                        raw_transcript="",  # 科技模式不需要 transcript
                        cleaned_transcript=json.dumps(analysis_data, ensure_ascii=False),
                        analysis=AnalysisDetail(
                            hook="",  # 科技模式不使用这些字段
                            core="",
                            cta="",
                            key_quotes=None,
                        ),
                    )

                # V2.0 通用叙事模式
                # 处理 LLM 可能返回结构化对象而非字符串的情况
                def to_string(value):
                    """将值转换为字符串，如果是 dict 则转为 JSON 字符串"""
                    if isinstance(value, dict):
                        return json.dumps(value, ensure_ascii=False)
                    return str(value)

                # 提取 analysis 对象（支持 V3.0 key_quotes）
                analysis_obj = analysis_data["analysis"]
                key_quotes = None
                if "key_quotes" in analysis_obj:
                    # V3.0: 提取 key_quotes 数组
                    quotes = analysis_obj["key_quotes"]
                    if isinstance(quotes, list):
                        key_quotes = [str(q) for q in quotes if q]  # 确保所有元素都是字符串

                return AnalysisResult(
                    raw_transcript=analysis_data["raw_transcript"],
                    cleaned_transcript=analysis_data["cleaned_transcript"],
                    analysis=AnalysisDetail(
                        hook=to_string(analysis_obj["hook"]),
                        core=to_string(analysis_obj["core"]),
                        cta=to_string(analysis_obj["cta"]),
                        key_quotes=key_quotes,
                    ),
                )
            except (json.JSONDecodeError, KeyError) as e:
                # 记录原始响应以便调试
                print(f"[DEBUG] DeepSeek raw response (first 500 chars): {content[:500]}")
                raise LLMError(f"Failed to parse DeepSeek response: {str(e)}. Response preview: {content[:200]}") from e

        except Exception as e:
            if isinstance(e, LLMError):
                raise

            # 提供更详细的错误信息
            import httpx
            if isinstance(e, (httpx.TimeoutException, httpx.ReadTimeout)):
                raise LLMError(f"DeepSeek API timeout: Request took too long (>{TimeoutConfig.LLM_TIMEOUT}s). Try without VPN or increase timeout.") from e
            elif isinstance(e, httpx.ConnectError):
                raise LLMError(f"DeepSeek API connection error: Cannot reach {self.base_url}. Check VPN or network settings.") from e
            elif isinstance(e, httpx.HTTPStatusError):
                raise LLMError(f"DeepSeek API HTTP error: {e.response.status_code} - {e.response.text[:200]}") from e
            else:
                raise LLMError(f"DeepSeek API error: {type(e).__name__}: {str(e)}") from e


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
                    "max_tokens": 4000,
                },
                timeout=TimeoutConfig.LLM_TIMEOUT,
            )

            response.raise_for_status()
            result = response.json()

            # 提取响应内容
            content = result["choices"][0]["message"]["content"]
            print(f"[DEBUG] Kimi API response received, content length: {len(content)}")

            # 解析JSON响应 (支持 V2.2 格式)
            try:
                # 移除可能的 markdown 代码块标记
                cleaned_content = content.strip()
                if cleaned_content.startswith("```json"):
                    cleaned_content = cleaned_content[7:]
                elif cleaned_content.startswith("```"):
                    cleaned_content = cleaned_content[3:]
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]
                cleaned_content = cleaned_content.strip()

                analysis_data = json.loads(cleaned_content)

                # V3.0: 检查是否为科技评测响应格式
                if "schema_type" in analysis_data and analysis_data["schema_type"] == "v3_tech_spec":
                    # V3.0 科技评测模式：直接返回 JSON 字符串供路由器解析
                    # 将 JSON 对象转为字符串存储在 cleaned_transcript 中
                    return AnalysisResult(
                        raw_transcript="",  # 科技模式不需要 transcript
                        cleaned_transcript=json.dumps(analysis_data, ensure_ascii=False),
                        analysis=AnalysisDetail(
                            hook="",  # 科技模式不使用这些字段
                            core="",
                            cta="",
                            key_quotes=None,
                        ),
                    )

                # V2.0 通用叙事模式
                # 处理 LLM 可能返回结构化对象而非字符串的情况
                def to_string(value):
                    """将值转换为字符串，如果是 dict 则转为 JSON 字符串"""
                    if isinstance(value, dict):
                        return json.dumps(value, ensure_ascii=False)
                    return str(value)

                # 提取 analysis 对象（支持 V3.0 key_quotes）
                analysis_obj = analysis_data["analysis"]
                key_quotes = None
                if "key_quotes" in analysis_obj:
                    # V3.0: 提取 key_quotes 数组
                    quotes = analysis_obj["key_quotes"]
                    if isinstance(quotes, list):
                        key_quotes = [str(q) for q in quotes if q]  # 确保所有元素都是字符串

                return AnalysisResult(
                    raw_transcript=analysis_data["raw_transcript"],
                    cleaned_transcript=analysis_data["cleaned_transcript"],
                    analysis=AnalysisDetail(
                        hook=to_string(analysis_obj["hook"]),
                        core=to_string(analysis_obj["core"]),
                        cta=to_string(analysis_obj["cta"]),
                        key_quotes=key_quotes,
                    ),
                )
            except (json.JSONDecodeError, KeyError) as e:
                # 记录原始响应以便调试
                print(f"[DEBUG] Kimi raw response (first 500 chars): {content[:500]}")
                raise LLMError(f"Failed to parse Kimi response: {str(e)}. Response preview: {content[:200]}") from e

        except Exception as e:
            if isinstance(e, LLMError):
                raise

            # 提供更详细的错误信息
            import httpx
            if isinstance(e, httpx.TimeoutException):
                raise LLMError(f"Kimi API timeout: Request took too long (>{TimeoutConfig.LLM_TIMEOUT}s)") from e
            elif isinstance(e, httpx.ConnectError):
                raise LLMError(f"Kimi API connection error: Cannot reach {self.base_url}. Check VPN or network settings.") from e
            elif isinstance(e, httpx.HTTPStatusError):
                raise LLMError(f"Kimi API HTTP error: {e.response.status_code} - {e.response.text[:200]}") from e
            else:
                raise LLMError(f"Kimi API error: {type(e).__name__}: {str(e)}") from e


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
        primary_error = None
        fallback_error = None

        # 尝试主服务 (Kimi)
        try:
            return await self.primary.analyze(text)
        except LLMError as e:
            primary_error = str(e)
            # 主服务失败，尝试备用服务 (DeepSeek)
            try:
                return await self.fallback.analyze(text)
            except LLMError as e:
                fallback_error = str(e)
                # 所有服务都失败
                raise LLMError(
                    f"All LLM services failed.\n"
                    f"Primary (Kimi) error: {primary_error}\n"
                    f"Fallback (DeepSeek) error: {fallback_error}"
                ) from e


def create_llm_router_from_env() -> LLMRouter:
    """
    从环境变量创建LLM路由器

    Returns:
        配置好的LLM路由器实例

    Raises:
        ValueError: 当必需的环境变量未设置时
    """
    # 创建Kimi适配器作为主服务
    primary = KimiAdapter()

    # 创建DeepSeek适配器作为备用服务
    fallback = DeepSeekAdapter()

    return LLMRouter(primary=primary, fallback=fallback)
