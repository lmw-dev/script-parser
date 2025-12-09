"""
ASR 服务工厂

根据环境变量 ASR_BACKEND 选择使用的 ASR 后端：
- dashscope: 使用 DashScope API（默认，不支持热词）
- nls: 使用智能语音交互 REST API（支持热词）
"""

import logging
import os
from pathlib import Path
from typing import Protocol

from .oss_uploader import OSSUploader

logger = logging.getLogger(__name__)


class ASRServiceProtocol(Protocol):
    """ASR 服务协议，定义统一接口"""
    
    async def transcribe_from_url(
        self, video_url: str, analysis_mode: str = "general"
    ) -> str:
        """从 URL 转录"""
        ...
    
    async def transcribe_from_file(
        self, file_path: Path, analysis_mode: str = "general"
    ) -> str:
        """从文件转录"""
        ...


def create_asr_service(
    oss_uploader: OSSUploader | None = None,
) -> ASRServiceProtocol:
    """
    创建 ASR 服务实例
    
    根据环境变量 ASR_BACKEND 选择后端：
    - dashscope (默认): DashScope API，快速但不支持热词
    - nls: 智能语音交互 REST API，支持热词功能
    
    Args:
        oss_uploader: OSS 上传器实例
        
    Returns:
        ASR 服务实例
        
    Raises:
        ValueError: 当后端配置无效或缺少必要凭证时
    """
    backend = os.getenv("ASR_BACKEND", "dashscope").lower().strip()
    
    logger.info(f"🔧 [ASR Factory] 创建 ASR 服务: backend={backend}")
    
    if backend == "nls":
        # 使用智能语音交互 REST API（支持热词）
        from .asr_nls_service import NLSASRService
        
        service = NLSASRService(oss_uploader=oss_uploader)
        logger.info("✅ [ASR Factory] 已创建 NLS ASR 服务（支持热词）")
        return service
    
    elif backend == "dashscope":
        # 使用 DashScope API（默认）
        from .asr_service import ASRService
        
        service = ASRService(oss_uploader=oss_uploader)
        logger.info("✅ [ASR Factory] 已创建 DashScope ASR 服务")
        return service
    
    else:
        raise ValueError(
            f"不支持的 ASR 后端: {backend}。"
            f"支持的选项: dashscope, nls"
        )


# 导出异常类，方便统一处理
from .asr_service import ASRError
from .asr_nls_service import NLSASRError

__all__ = [
    "create_asr_service",
    "ASRServiceProtocol",
    "ASRError",
    "NLSASRError",
]

