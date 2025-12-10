"""
阿里云智能语音交互 ASR 服务适配器
使用阿里云官方 SDK 实现，支持热词功能

参考文档：
- SDK和API概览: https://help.aliyun.com/zh/isi/getting-started/sdk-and-api-references
- 录音文件识别接口说明: https://help.aliyun.com/zh/isi/developer-reference/api-reference-2
- Python SDK: https://help.aliyun.com/zh/isi/developer-reference/sdk-for-python-3
"""

import asyncio
import json
import logging
import os
import time
from http import HTTPStatus
from pathlib import Path
from typing import Any
from urllib import request

from ..config import TimeoutConfig
from .oss_uploader import OSSUploader, OSSUploaderError

# 配置日志
logger = logging.getLogger(__name__)

# 尝试导入阿里云 SDK
try:
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
    ALIYUN_SDK_AVAILABLE = True
except ImportError:
    ALIYUN_SDK_AVAILABLE = False
    logger.warning("⚠️ aliyunsdkcore 未安装，NLS ASR 服务不可用。请运行: pip install aliyun-python-sdk-core")


class NLSASRError(Exception):
    """智能语音交互 ASR 服务错误"""
    pass


class NLSASRService:
    """
    阿里云智能语音交互 ASR 服务
    
    支持热词功能，通过 vocabulary_id 参数注入热词表
    使用阿里云官方 SDK 处理签名
    """
    
    def __init__(
        self,
        oss_uploader: OSSUploader | None = None,
        access_key_id: str | None = None,
        access_key_secret: str | None = None,
        appkey: str | None = None,
    ):
        """
        初始化智能语音交互 ASR 服务
        
        Args:
            oss_uploader: OSS上传器实例，用于上传本地文件
            access_key_id: 阿里云 AccessKey ID
            access_key_secret: 阿里云 AccessKey Secret
            appkey: 智能语音交互项目 AppKey
            
        Raises:
            ValueError: 当必要的凭证未设置时
        """
        if not ALIYUN_SDK_AVAILABLE:
            raise ValueError(
                "aliyunsdkcore 未安装。请运行: pip install aliyun-python-sdk-core"
            )
        
        self.oss_uploader = oss_uploader
        
        # 从环境变量或参数获取凭证
        self.access_key_id = access_key_id or os.getenv("ALIYUN_ACCESS_KEY_ID", "").strip()
        self.access_key_secret = access_key_secret or os.getenv("ALIYUN_ACCESS_KEY_SECRET", "").strip()
        self.appkey = appkey or os.getenv("ALIYUN_NLS_APPKEY", "").strip()
        
        # 验证必要的凭证
        if not self.access_key_id:
            raise ValueError("ALIYUN_ACCESS_KEY_ID environment variable not set")
        if not self.access_key_secret:
            raise ValueError("ALIYUN_ACCESS_KEY_SECRET environment variable not set")
        if not self.appkey:
            raise ValueError("ALIYUN_NLS_APPKEY environment variable not set")
        
        # 创建阿里云客户端
        self.client = AcsClient(
            self.access_key_id,
            self.access_key_secret,
            "cn-shanghai"
        )
        
        logger.info(f"🔧 [NLS-ASR] 初始化完成: appkey={self.appkey[:8]}...")
    
    def _create_common_request(self, action: str) -> CommonRequest:
        """创建通用请求对象"""
        req = CommonRequest()
        req.set_domain("filetrans.cn-shanghai.aliyuncs.com")
        req.set_version("2018-08-17")
        req.set_action_name(action)
        req.set_method("POST")
        req.set_protocol_type("https")
        return req
    
    async def _submit_task(
        self, 
        file_url: str, 
        vocabulary_id: str | None = None
    ) -> str:
        """
        提交录音文件识别任务
        
        Args:
            file_url: 音频文件 URL
            vocabulary_id: 热词表 ID（可选）
            
        Returns:
            任务 ID
        """
        # 构建任务参数
        task_config = {
            "appkey": self.appkey,
            "file_link": file_url,
            "version": "4.0",
            "enable_words": False,
            "enable_sample_rate_adaptive": True,
            # 启用逆文本正则化(ITN)：将中文数字转为阿拉伯数字，合并拼读字母
            "enable_inverse_text_normalization": True,
        }
        
        # 添加热词表
        if vocabulary_id:
            task_config["vocabulary_id"] = vocabulary_id
            logger.info(f"🔧 [NLS-ASR] 热词表已注入: vocabulary_id={vocabulary_id}")
        
        # 创建请求 - NLS API 要求参数放在查询字符串中
        req = self._create_common_request("SubmitTask")
        req.add_query_param("Task", json.dumps(task_config, separators=(',', ':')))
        
        try:
            # 使用 asyncio.to_thread 在后台线程执行同步 SDK 调用
            response = await asyncio.to_thread(
                self.client.do_action_with_exception, req
            )
            result = json.loads(response)
            
            status_code = result.get("StatusCode")
            if status_code != 21050000:
                error_msg = result.get("StatusText", "Unknown error")
                raise NLSASRError(f"提交任务失败: {status_code} - {error_msg}")
            
            task_id = result.get("TaskId")
            if not task_id:
                raise NLSASRError("提交任务成功但未返回 TaskId")
            
            logger.info(f"🔧 [NLS-ASR] 任务已提交: task_id={task_id}")
            return task_id
            
        except Exception as e:
            if isinstance(e, NLSASRError):
                raise
            raise NLSASRError(f"提交任务失败: {str(e)}") from e
    
    async def _query_task(self, task_id: str) -> dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务状态信息
        """
        req = self._create_common_request("GetTaskResult")
        req.set_method("GET")  # 查询任务状态使用 GET 方法
        req.add_query_param("TaskId", task_id)
        
        try:
            response = await asyncio.to_thread(
                self.client.do_action_with_exception, req
            )
            return json.loads(response)
        except Exception as e:
            raise NLSASRError(f"查询任务失败: {str(e)}") from e
    
    def _format_transcript_with_paragraphs(self, sentences: list[dict]) -> str:
        """
        将 NLS API 返回的句子数组格式化为带分段的文本
        
        分段策略：
        1. 根据句子间的静音时长分段（>1.5秒认为是段落边界）
        2. 每累积约200-300字自动分段（避免段落过长）
        3. 遇到语气词结尾（？！。）也会考虑分段
        
        Args:
            sentences: NLS API 返回的句子数组，每个句子包含 Text, BeginTime, EndTime 等
            
        Returns:
            格式化后的带分段文本
        """
        if not sentences:
            return ""
        
        paragraphs = []
        current_paragraph = []
        current_char_count = 0
        
        # 分段阈值
        SILENCE_THRESHOLD_MS = 1500  # 静音超过1.5秒分段
        CHAR_THRESHOLD = 250  # 字符数阈值
        
        for i, sentence in enumerate(sentences):
            text = sentence.get("Text", "").strip()
            if not text:
                continue
            
            current_paragraph.append(text)
            current_char_count += len(text)
            
            # 判断是否需要分段
            should_break = False
            
            # 条件1: 检查与下一句的时间间隔
            if i < len(sentences) - 1:
                current_end = sentence.get("EndTime", 0)
                next_begin = sentences[i + 1].get("BeginTime", 0)
                silence_duration = next_begin - current_end
                
                if silence_duration >= SILENCE_THRESHOLD_MS:
                    should_break = True
                    logger.debug(f"🔧 [NLS-ASR] 静音分段: {silence_duration}ms")
            
            # 条件2: 字符数超过阈值，且当前句子以句号/问号/感叹号结尾
            if current_char_count >= CHAR_THRESHOLD:
                if text.endswith(('。', '？', '！', '?', '!', '.', '…')):
                    should_break = True
                    logger.debug(f"🔧 [NLS-ASR] 长度分段: {current_char_count}字符")
            
            # 条件3: 字符数严重超标，强制分段
            if current_char_count >= CHAR_THRESHOLD * 1.5:
                should_break = True
                logger.debug(f"🔧 [NLS-ASR] 强制分段: {current_char_count}字符")
            
            # 执行分段
            if should_break and current_paragraph:
                paragraphs.append("".join(current_paragraph))
                current_paragraph = []
                current_char_count = 0
        
        # 添加最后一个段落
        if current_paragraph:
            paragraphs.append("".join(current_paragraph))
        
        # 用双换行符连接段落
        transcript = "\n\n".join(paragraphs)
        logger.info(f"🔧 [NLS-ASR] 分段完成: {len(paragraphs)} 段，共 {len(transcript)} 字符")
        
        return transcript
    
    async def _wait_for_result(self, task_id: str, timeout: float) -> str:
        """
        等待任务完成并获取结果
        
        Args:
            task_id: 任务 ID
            timeout: 超时时间（秒）
            
        Returns:
            转录文本
        """
        start_time = time.time()
        poll_interval = 3  # 轮询间隔（秒）
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise NLSASRError(f"任务超时: 已等待 {elapsed:.1f} 秒")
            
            result = await self._query_task(task_id)
            status_code = result.get("StatusCode")
            status_text = result.get("StatusText", "")
            
            # 21050000: 成功
            # 21050001: 任务进行中
            # 21050002: 任务排队中
            if status_code == 21050000:
                # 任务完成
                task_result = result.get("Result", {})
                sentences = task_result.get("Sentences", [])
                
                if not sentences:
                    return ""
                
                # 智能分段处理
                transcript = self._format_transcript_with_paragraphs(sentences)
                logger.info(f"🔧 [NLS-ASR] 转录完成: {len(transcript)} 字符")
                return transcript
            
            elif status_code in [21050001, 21050002]:
                # 任务进行中或排队中
                logger.info(f"🔧 [NLS-ASR] 任务状态: {status_text} (已等待 {elapsed:.1f}s)")
                await asyncio.sleep(poll_interval)
            
            else:
                # 任务失败
                raise NLSASRError(f"任务失败: {status_code} - {status_text}")
    
    async def transcribe_from_url(
        self, 
        video_url: str, 
        analysis_mode: str = "general"
    ) -> str:
        """
        从视频 URL 转录文本
        
        Args:
            video_url: 视频文件 URL
            analysis_mode: 分析模式 ("general" 或 "tech")
                          - "general": 通用叙事分析，不使用热词
                          - "tech": 科技产品评测，注入科技热词表
            
        Returns:
            转录的文本内容
            
        Raises:
            NLSASRError: 当转录失败时
        """
        logger.info(f"🔧 [NLS-ASR] 开始转录: mode={analysis_mode}")
        
        # 获取热词表 ID
        vocabulary_id = None
        if analysis_mode == "tech":
            vocabulary_id = os.getenv("ALIYUN_TECH_HOTWORD_ID", "").strip()
            if vocabulary_id:
                logger.info(f"🔧 [NLS-ASR] 科技模式: 使用热词表 {vocabulary_id}")
            else:
                logger.warning("⚠️ [NLS-ASR] 科技模式: 未配置热词表 ALIYUN_TECH_HOTWORD_ID")
        
        try:
            # 提交任务
            task_id = await self._submit_task(video_url, vocabulary_id)
            
            # 等待结果
            transcript = await self._wait_for_result(task_id, TimeoutConfig.ASR_TIMEOUT)
            
            return transcript
            
        except Exception as e:
            if isinstance(e, NLSASRError):
                raise
            raise NLSASRError(f"转录失败: {str(e)}") from e
    
    async def transcribe_from_file(
        self, 
        file_path: Path, 
        analysis_mode: str = "general"
    ) -> str:
        """
        从本地文件转录文本
        
        需要配置 OSS 上传器，会先将文件上传到 OSS
        
        Args:
            file_path: 本地文件路径
            analysis_mode: 分析模式
            
        Returns:
            转录的文本内容
        """
        if not self.oss_uploader:
            raise NLSASRError("需要配置 OSS 上传器才能转录本地文件")
        
        try:
            # 上传文件到 OSS
            upload_result = self.oss_uploader.upload_file(file_path)
            logger.info(f"🔧 [NLS-ASR] 文件已上传: {upload_result.file_url}")
            
            # 使用 URL 转录
            return await self.transcribe_from_url(upload_result.file_url, analysis_mode)
            
        except OSSUploaderError as e:
            raise NLSASRError(f"上传文件失败: {e}") from e

