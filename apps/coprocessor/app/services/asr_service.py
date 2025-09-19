"""
阿里云通义听悟ASR服务适配器
基于 dashscope 库实现
"""

import json
import os
from http import HTTPStatus
from pathlib import Path
from urllib import request

import dashscope

from .oss_uploader import OSSUploader, OSSUploaderError


class ASRError(Exception):
    """Custom exception for ASR service errors."""

    pass


class ASRService:
    """阿里云通义听悟ASR服务"""

    def __init__(
        self,
        oss_uploader: OSSUploader | None = None,
        api_key: str = None,
        model: str = "paraformer-v2",
    ):
        """
        初始化ASR服务

        Args:
            oss_uploader: OSS上传器实例，用于上传本地文件。如果为None，则使用传统模式
            api_key: 阿里云API密钥，如果为None则从环境变量获取
            model: ASR模型名称，默认为paraformer-v2

        Raises:
            ValueError: 当API密钥未设置时
        """
        self.oss_uploader = oss_uploader

        # 尝试多个可能的环境变量名
        self.api_key = (
            api_key or os.getenv("DASHSCOPE_API_KEY") or os.getenv("ALIYUN_ASR_API_KEY")
        )
        if not self.api_key:
            raise ValueError(
                "DASHSCOPE_API_KEY or ALIYUN_ASR_API_KEY environment variable not set."
            )

        dashscope.api_key = self.api_key
        self.model = model

    async def transcribe_from_url(self, video_url: str) -> str:
        """
        从视频URL转录文本

        Args:
            video_url: 视频文件URL

        Returns:
            转录的文本内容

        Raises:
            ASRError: 当转录失败时
        """
        try:
            # 发起异步转录任务
            task_response = dashscope.audio.asr.Transcription.async_call(
                model=self.model, file_urls=[video_url], language_hints=["zh", "en"]
            )

            # 检查响应是否有效
            if (
                not task_response
                or not hasattr(task_response, "output")
                or not task_response.output
            ):
                raise ASRError(
                    "Invalid response from DashScope API - check your API key"
                )

            if not hasattr(task_response.output, "task_id"):
                error_msg = getattr(task_response, "message", "Unknown error")
                status_code = getattr(task_response, "status_code", "Unknown")
                raise ASRError(
                    f"DashScope API error (status: {status_code}): {error_msg}"
                )

            # 等待转录完成
            transcription_response = dashscope.audio.asr.Transcription.wait(
                task=task_response.output.task_id
            )

            # 处理转录结果
            return self._process_transcription_response(transcription_response)

        except Exception as e:
            if isinstance(e, ASRError):
                raise
            raise ASRError(f"ASR service error: {str(e)}") from e

    async def transcribe_from_file(self, file_path: Path) -> str:
        """
        从本地文件转录文本

        如果配置了OSS上传器，会先将文件上传到OSS，然后使用公开URL进行转录。
        如果没有配置OSS上传器，会尝试使用绝对路径（传统模式，通常会失败）。

        Args:
            file_path: 本地文件路径

        Returns:
            转录的文本内容

        Raises:
            ASRError: 当转录失败时
        """
        try:
            # 如果配置了OSS上传器，使用OSS模式
            if self.oss_uploader:
                try:
                    upload_result = self.oss_uploader.upload_file(file_path)
                    return await self.transcribe_from_url(upload_result.file_url)
                except OSSUploaderError as e:
                    raise ASRError(
                        f"Failed to upload file to OSS before transcription: {e}"
                    ) from e
                except Exception as e:
                    raise ASRError(
                        f"An unexpected error occurred during file transcription: {e}"
                    ) from e

            # 传统模式：使用绝对路径尝试转录
            abs_path = str(file_path.resolve())

            # 发起异步转录任务
            task_response = dashscope.audio.asr.Transcription.async_call(
                model=self.model,
                file_urls=[abs_path],
                language_hints=["zh", "en"],
            )

            # 检查响应是否有效
            if (
                not task_response
                or not hasattr(task_response, "output")
                or not task_response.output
            ):
                raise ASRError(
                    "Invalid response from DashScope API - check your API key"
                )

            if not hasattr(task_response.output, "task_id"):
                error_msg = getattr(task_response, "message", "Unknown error")
                status_code = getattr(task_response, "status_code", "Unknown")
                raise ASRError(
                    f"DashScope API error (status: {status_code}): {error_msg}"
                )

            # 等待转录完成
            transcription_response = dashscope.audio.asr.Transcription.wait(
                task=task_response.output.task_id
            )

            # 处理转录结果
            return self._process_transcription_response(transcription_response)

        except Exception as e:
            if isinstance(e, ASRError):
                raise
            # 检查是否是文件下载失败的错误
            error_str = str(e)
            if "FILE_DOWNLOAD_FAILED" in error_str:
                raise ASRError(
                    "DashScope cannot access local files. Please upload the file to a publicly accessible URL and use transcribe_from_url() instead."
                ) from e
            raise ASRError(f"ASR service error: {error_str}") from e

    def _process_transcription_response(self, response) -> str:
        """
        处理转录响应，提取文本内容

        Args:
            response: dashscope转录响应对象

        Returns:
            提取的文本内容

        Raises:
            ASRError: 当处理响应失败时
        """
        try:
            if response.status_code != HTTPStatus.OK:
                error_msg = getattr(response.output, "message", "Unknown error")
                raise ASRError(f"Transcription failed: {error_msg}")

            # 获取转录结果URL
            results = response.output.get("results", [])
            if not results:
                raise ASRError("No transcription results returned")

            # 检查第一个结果的内容
            first_result = results[0]
            if not isinstance(first_result, dict):
                raise ASRError(f"Invalid result format: {type(first_result)}")

            # 检查是否是失败的任务
            if first_result.get("subtask_status") == "FAILED":
                error_code = first_result.get("code", "Unknown")
                error_message = first_result.get("message", "Unknown error")
                if error_code == "FILE_DOWNLOAD_FAILED":
                    raise ASRError(
                        "DashScope cannot access the file. Please ensure the file is publicly accessible via URL."
                    )
                else:
                    raise ASRError(
                        f"Transcription failed: {error_code} - {error_message}"
                    )

            if "transcription_url" not in first_result:
                available_keys = list(first_result.keys())
                raise ASRError(
                    f"No transcription_url in result. Available keys: {available_keys}"
                )

            transcription_url = first_result["transcription_url"]

            # 下载并解析转录结果
            result_response = request.urlopen(transcription_url)
            result_data = json.loads(result_response.read().decode("utf8"))

            # 提取文本内容
            transcripts = result_data.get("transcripts", [])
            if not transcripts:
                return ""  # 返回空字符串表示没有识别到内容

            # 获取第一个转录通道的文本
            first_transcript = transcripts[0]
            if isinstance(first_transcript, dict) and "text" in first_transcript:
                return first_transcript["text"]
            else:
                raise ASRError(f"Invalid transcript format: {first_transcript}")

        except json.JSONDecodeError as e:
            raise ASRError(f"Failed to parse transcription result: {str(e)}") from e
        except Exception as e:
            if isinstance(e, ASRError):
                raise
            raise ASRError(f"Failed to process transcription response: {str(e)}") from e
