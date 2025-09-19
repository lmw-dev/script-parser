"""
ASR Service 与 OSS Uploader 集成测试
验证完整的文件上传和转录流程
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from .asr_service import ASRError, ASRService
from .oss_uploader import OSSUploaderError, OSSUploadResult


class TestASROSSIntegration:
    """ASR Service 与 OSS Uploader 集成测试"""

    def test_asr_service_with_oss_uploader_initialization(self):
        """测试带OSS上传器的ASR服务初始化"""
        mock_oss_uploader = Mock()
        service = ASRService(oss_uploader=mock_oss_uploader, api_key="test-key")

        assert service.oss_uploader is mock_oss_uploader
        assert service.api_key == "test-key"
        assert service.model == "paraformer-v2"

    def test_asr_service_without_oss_uploader_initialization(self):
        """测试不带OSS上传器的ASR服务初始化（传统模式）"""
        service = ASRService(api_key="test-key")

        assert service.oss_uploader is None
        assert service.api_key == "test-key"
        assert service.model == "paraformer-v2"

    @pytest.mark.asyncio
    async def test_transcribe_from_file_oss_integration_flow(self, mocker):
        """测试完整的OSS集成转录流程"""
        # 1. 创建Mock OSS上传器
        mock_oss_uploader = Mock()
        mock_upload_result = OSSUploadResult(
            file_url="https://test-bucket.oss-cn-beijing.aliyuncs.com/audio/123_test.mp4",
            object_key="audio/123_test.mp4",
        )
        mock_oss_uploader.upload_file.return_value = mock_upload_result

        # 2. Mock ASR服务的transcribe_from_url方法
        mock_transcribe_from_url = mocker.patch.object(
            ASRService, "transcribe_from_url", return_value="集成测试转录结果"
        )

        # 3. 创建ASR服务实例
        service = ASRService(oss_uploader=mock_oss_uploader, api_key="test-key")

        # 4. 执行文件转录
        test_file_path = Path("/tmp/test_video.mp4")
        result = await service.transcribe_from_file(test_file_path)

        # 5. 验证结果
        assert result == "集成测试转录结果"

        # 6. 验证调用链
        mock_oss_uploader.upload_file.assert_called_once_with(test_file_path)
        mock_transcribe_from_url.assert_called_once_with(
            "https://test-bucket.oss-cn-beijing.aliyuncs.com/audio/123_test.mp4"
        )

    @pytest.mark.asyncio
    async def test_transcribe_from_file_oss_error_handling(self, mocker):
        """测试OSS上传错误的处理"""
        # 1. 创建Mock OSS上传器，模拟上传失败
        mock_oss_uploader = Mock()
        mock_oss_uploader.upload_file.side_effect = OSSUploaderError("上传失败")

        # 2. 创建ASR服务实例
        service = ASRService(oss_uploader=mock_oss_uploader, api_key="test-key")

        # 3. 执行文件转录，期望抛出ASRError
        test_file_path = Path("/tmp/test_video.mp4")

        with pytest.raises(
            ASRError, match="Failed to upload file to OSS before transcription"
        ):
            await service.transcribe_from_file(test_file_path)

        # 4. 验证OSS上传器被调用
        mock_oss_uploader.upload_file.assert_called_once_with(test_file_path)

    @pytest.mark.asyncio
    async def test_transcribe_from_file_fallback_to_legacy_mode(self, mocker):
        """测试在没有OSS上传器时回退到传统模式"""
        # 1. Mock dashscope API调用
        mock_async_call = mocker.patch("dashscope.audio.asr.Transcription.async_call")
        mock_wait = mocker.patch("dashscope.audio.asr.Transcription.wait")

        # 2. Mock _process_transcription_response方法
        mock_process_response = mocker.patch.object(
            ASRService,
            "_process_transcription_response",
            return_value="传统模式转录结果",
        )

        # 3. 设置Mock响应
        mock_task_response = Mock()
        mock_task_response.output.task_id = "test-task-legacy"
        mock_async_call.return_value = mock_task_response

        mock_transcription_response = Mock()
        mock_wait.return_value = mock_transcription_response

        # 4. 创建不带OSS上传器的ASR服务实例
        service = ASRService(api_key="test-key")

        # 5. 执行文件转录
        test_file_path = Path("/tmp/test_video.mp4")
        result = await service.transcribe_from_file(test_file_path)

        # 6. 验证结果
        assert result == "传统模式转录结果"

        # 7. 验证调用了传统模式的API
        mock_async_call.assert_called_once_with(
            model="paraformer-v2",
            file_urls=[str(test_file_path.resolve())],
            language_hints=["zh", "en"],
        )
        mock_wait.assert_called_once_with(task="test-task-legacy")
        mock_process_response.assert_called_once_with(mock_transcription_response)
