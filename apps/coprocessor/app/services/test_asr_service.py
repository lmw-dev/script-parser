import json
from http import HTTPStatus
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from .asr_service import ASRError, ASRService
from .oss_uploader import OSSUploaderError, OSSUploadResult


class TestASRService:
    """Test cases for ASRService class"""

    def test_init_with_api_key(self):
        """Test successful initialization with API key"""
        service = ASRService(api_key="test-api-key")
        assert service.api_key == "test-api-key"
        assert service.model == "paraformer-v2"

    def test_init_with_custom_model(self):
        """Test initialization with custom model"""
        service = ASRService(api_key="test-api-key", model="custom-model")
        assert service.model == "custom-model"

    def test_init_missing_api_key_raises_error(self):
        """Test that missing API key raises ValueError"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(
                ValueError,
                match="DASHSCOPE_API_KEY or ALIYUN_ASR_API_KEY environment variable not set",
            ):
                ASRService()

    @patch.dict("os.environ", {"DASHSCOPE_API_KEY": "env-api-key"})
    def test_init_from_environment(self):
        """Test initialization from environment variable"""
        service = ASRService()
        assert service.api_key == "env-api-key"

    @pytest.mark.asyncio
    async def test_transcribe_from_url_success(self, mocker):
        """Test successful transcription from URL"""
        # Mock dashscope API calls
        mock_async_call = mocker.patch("dashscope.audio.asr.Transcription.async_call")
        mock_wait = mocker.patch("dashscope.audio.asr.Transcription.wait")
        mock_urlopen = mocker.patch("urllib.request.urlopen")

        # Setup mock responses
        mock_task_response = Mock()
        mock_task_response.output.task_id = "test-task-123"
        mock_async_call.return_value = mock_task_response

        mock_transcription_response = Mock()
        mock_transcription_response.status_code = HTTPStatus.OK
        mock_transcription_response.output = {
            "results": [{"transcription_url": "https://example.com/result.json"}]
        }
        mock_wait.return_value = mock_transcription_response

        # Mock the JSON response from transcription URL
        mock_json_response = {"transcripts": [{"text": "这是测试转录文本"}]}
        mock_response = Mock()
        mock_response.read.return_value.decode.return_value = json.dumps(
            mock_json_response
        )
        mock_urlopen.return_value = mock_response

        # Test the service
        service = ASRService(api_key="test-api-key")
        result = await service.transcribe_from_url("https://example.com/video.mp4")

        # Assertions
        assert result == "这是测试转录文本"
        mock_async_call.assert_called_once_with(
            model="paraformer-v2",
            file_urls=["https://example.com/video.mp4"],
            language_hints=["zh", "en"],
        )
        mock_wait.assert_called_once_with(task="test-task-123")

    @pytest.mark.asyncio
    async def test_transcribe_from_file_with_oss_integration_success(self, mocker):
        """Test successful transcription from file using OSS integration"""
        # Mock OSS uploader
        mock_oss_uploader = Mock()
        mock_upload_result = OSSUploadResult(
            file_url="http://fake-oss-url.com/video.mp4",
            object_key="audio/123456789_test_video.mp4",
        )
        mock_oss_uploader.upload_file.return_value = mock_upload_result

        # Mock dashscope API calls
        mock_async_call = mocker.patch("dashscope.audio.asr.Transcription.async_call")
        mock_wait = mocker.patch("dashscope.audio.asr.Transcription.wait")
        mock_urlopen = mocker.patch("urllib.request.urlopen")

        # Setup mock responses
        mock_task_response = Mock()
        mock_task_response.output.task_id = "test-task-oss-456"
        mock_async_call.return_value = mock_task_response

        mock_transcription_response = Mock()
        mock_transcription_response.status_code = HTTPStatus.OK
        mock_transcription_response.output = {
            "results": [{"transcription_url": "https://example.com/result.json"}]
        }
        mock_wait.return_value = mock_transcription_response

        # Mock the JSON response from transcription URL
        mock_json_response = {"transcripts": [{"text": "这是OSS集成转录文本"}]}
        mock_response = Mock()
        mock_response.read.return_value.decode.return_value = json.dumps(
            mock_json_response
        )
        mock_urlopen.return_value = mock_response

        # Test the service with OSS uploader
        service = ASRService(oss_uploader=mock_oss_uploader, api_key="test-api-key")
        test_file_path = Path("/tmp/test_video.mp4")
        result = await service.transcribe_from_file(test_file_path)

        # Assertions
        assert result == "这是OSS集成转录文本"

        # Verify OSS uploader was called
        mock_oss_uploader.upload_file.assert_called_once_with(test_file_path)

        # Verify dashscope was called with the OSS URL
        mock_async_call.assert_called_once_with(
            model="paraformer-v2",
            file_urls=["http://fake-oss-url.com/video.mp4"],
            language_hints=["zh", "en"],
        )
        mock_wait.assert_called_once_with(task="test-task-oss-456")

    @pytest.mark.asyncio
    async def test_transcribe_from_file_oss_upload_error(self, mocker):
        """Test handling of OSS upload error during file transcription"""
        # Mock OSS uploader to raise error
        mock_oss_uploader = Mock()
        mock_oss_uploader.upload_file.side_effect = OSSUploaderError("Upload failed")

        # Test the service with OSS uploader
        service = ASRService(oss_uploader=mock_oss_uploader, api_key="test-api-key")
        test_file_path = Path("/tmp/test_video.mp4")

        with pytest.raises(
            ASRError, match="Failed to upload file to OSS before transcription"
        ):
            await service.transcribe_from_file(test_file_path)

        # Verify OSS uploader was called
        mock_oss_uploader.upload_file.assert_called_once_with(test_file_path)

    @pytest.mark.asyncio
    async def test_transcribe_from_file_legacy_mode_success(self, mocker):
        """Test successful transcription from file in legacy mode (without OSS)"""
        # Mock dashscope API calls
        mock_async_call = mocker.patch("dashscope.audio.asr.Transcription.async_call")
        mock_wait = mocker.patch("dashscope.audio.asr.Transcription.wait")
        mock_urlopen = mocker.patch("urllib.request.urlopen")

        # Setup mock responses
        mock_task_response = Mock()
        mock_task_response.output.task_id = "test-task-456"
        mock_async_call.return_value = mock_task_response

        mock_transcription_response = Mock()
        mock_transcription_response.status_code = HTTPStatus.OK
        mock_transcription_response.output = {
            "results": [{"transcription_url": "https://example.com/result.json"}]
        }
        mock_wait.return_value = mock_transcription_response

        # Mock the JSON response from transcription URL
        mock_json_response = {"transcripts": [{"text": "这是文件转录文本"}]}
        mock_response = Mock()
        mock_response.read.return_value.decode.return_value = json.dumps(
            mock_json_response
        )
        mock_urlopen.return_value = mock_response

        # Test the service without OSS uploader (legacy mode)
        service = ASRService(api_key="test-api-key")
        test_file_path = Path("/tmp/test_video.mp4")
        result = await service.transcribe_from_file(test_file_path)

        # Assertions
        assert result == "这是文件转录文本"
        mock_async_call.assert_called_once_with(
            model="paraformer-v2",
            file_urls=[str(test_file_path.resolve())],  # 使用解析后的绝对路径
            language_hints=["zh", "en"],
        )

    @pytest.mark.asyncio
    async def test_transcribe_from_url_api_failure(self, mocker):
        """Test API failure scenario"""
        # Mock dashscope API calls
        mock_async_call = mocker.patch("dashscope.audio.asr.Transcription.async_call")
        mock_wait = mocker.patch("dashscope.audio.asr.Transcription.wait")

        # Setup mock responses for failure
        mock_task_response = Mock()
        mock_task_response.output.task_id = "test-task-789"
        mock_async_call.return_value = mock_task_response

        mock_transcription_response = Mock()
        mock_transcription_response.status_code = HTTPStatus.BAD_REQUEST
        mock_transcription_response.output = {"message": "API Error"}
        mock_wait.return_value = mock_transcription_response

        # Test the service
        service = ASRService(api_key="test-api-key")

        with pytest.raises(ASRError, match="Transcription failed"):
            await service.transcribe_from_url("https://example.com/video.mp4")

    @pytest.mark.asyncio
    async def test_transcribe_from_url_network_error(self, mocker):
        """Test network error during API call"""
        # Mock dashscope API to raise exception
        mock_async_call = mocker.patch("dashscope.audio.asr.Transcription.async_call")
        mock_async_call.side_effect = Exception("Network error")

        # Test the service
        service = ASRService(api_key="test-api-key")

        with pytest.raises(ASRError, match="ASR service error"):
            await service.transcribe_from_url("https://example.com/video.mp4")

    @pytest.mark.asyncio
    async def test_transcribe_from_url_empty_transcripts(self, mocker):
        """Test handling of empty transcripts"""
        # Mock dashscope API calls
        mock_async_call = mocker.patch("dashscope.audio.asr.Transcription.async_call")
        mock_wait = mocker.patch("dashscope.audio.asr.Transcription.wait")
        mock_urlopen = mocker.patch("urllib.request.urlopen")

        # Setup mock responses
        mock_task_response = Mock()
        mock_task_response.output.task_id = "test-task-empty"
        mock_async_call.return_value = mock_task_response

        mock_transcription_response = Mock()
        mock_transcription_response.status_code = HTTPStatus.OK
        mock_transcription_response.output = {
            "results": [{"transcription_url": "https://example.com/result.json"}]
        }
        mock_wait.return_value = mock_transcription_response

        # Mock empty transcripts response
        mock_json_response = {"transcripts": []}
        mock_response = Mock()
        mock_response.read.return_value.decode.return_value = json.dumps(
            mock_json_response
        )
        mock_urlopen.return_value = mock_response

        # Test the service
        service = ASRService(api_key="test-api-key")
        result = await service.transcribe_from_url("https://example.com/video.mp4")

        # Should return empty string for no transcripts
        assert result == ""

    @pytest.mark.asyncio
    async def test_transcribe_from_url_json_parse_error(self, mocker):
        """Test JSON parsing error"""
        # Mock dashscope API calls
        mock_async_call = mocker.patch("dashscope.audio.asr.Transcription.async_call")
        mock_wait = mocker.patch("dashscope.audio.asr.Transcription.wait")
        mock_urlopen = mocker.patch("urllib.request.urlopen")

        # Setup mock responses
        mock_task_response = Mock()
        mock_task_response.output.task_id = "test-task-json-error"
        mock_async_call.return_value = mock_task_response

        mock_transcription_response = Mock()
        mock_transcription_response.status_code = HTTPStatus.OK
        mock_transcription_response.output = {
            "results": [{"transcription_url": "https://example.com/result.json"}]
        }
        mock_wait.return_value = mock_transcription_response

        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.read.return_value.decode.return_value = "invalid json"
        mock_urlopen.return_value = mock_response

        # Test the service
        service = ASRService(api_key="test-api-key")

        with pytest.raises(ASRError, match="Failed to parse transcription result"):
            await service.transcribe_from_url("https://example.com/video.mp4")


class TestASRError:
    """Test cases for ASRError exception"""

    def test_asr_error_creation(self):
        """Test ASRError exception creation"""
        error = ASRError("Test error message")
        assert str(error) == "Test error message"

    def test_asr_error_inheritance(self):
        """Test that ASRError inherits from Exception"""
        error = ASRError("Test error")
        assert isinstance(error, Exception)
