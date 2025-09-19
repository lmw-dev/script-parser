"""
Tests for service integration and dependency management optimizations
"""

import time
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.error_handling import ServiceInitializationError
from app.main import WorkflowOrchestrator
from app.services.asr_service import ASRError
from app.services.file_handler import TempFileInfo
from app.services.llm_service import AnalysisResult, LLMError
from app.services.oss_uploader import OSSUploaderError
from app.services.url_parser import VideoInfo


class TestWorkflowOrchestrator:
    """Test service integration in WorkflowOrchestrator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.orchestrator = WorkflowOrchestrator()

    def test_url_parser_initialization_success(self):
        """测试ShareURLParser正确初始化"""
        parser = self.orchestrator._get_url_parser()
        assert parser is not None

        # Test singleton behavior - should return same instance
        parser2 = self.orchestrator._get_url_parser()
        assert parser is parser2

    def test_file_handler_initialization_success(self):
        """测试FileHandler正确初始化"""
        handler = self.orchestrator._get_file_handler()
        assert handler is not None

        # Test singleton behavior - should return same instance
        handler2 = self.orchestrator._get_file_handler()
        assert handler is handler2

    @patch("app.main.create_oss_uploader_from_env")
    def test_oss_uploader_initialization_success(self, mock_create_oss):
        """测试OSSUploader正确初始化"""
        mock_uploader = Mock()
        mock_create_oss.return_value = mock_uploader

        uploader = self.orchestrator._get_oss_uploader()
        assert uploader is mock_uploader

        # Test singleton behavior - should return same instance
        uploader2 = self.orchestrator._get_oss_uploader()
        assert uploader is uploader2

        # Should only call factory function once
        mock_create_oss.assert_called_once()

    @patch("app.main.create_llm_router_from_env")
    def test_llm_router_initialization_success(self, mock_create_llm):
        """测试LLMRouter正确初始化"""
        mock_router = Mock()
        mock_create_llm.return_value = mock_router

        router = self.orchestrator._get_llm_router()
        assert router is mock_router

        # Test singleton behavior - should return same instance
        router2 = self.orchestrator._get_llm_router()
        assert router is router2

        # Should only call factory function once
        mock_create_llm.assert_called_once()

    @patch("app.main.create_oss_uploader_from_env")
    def test_oss_uploader_initialization_failure(self, mock_create_oss):
        """测试OSS上传器初始化失败的错误处理"""
        mock_create_oss.side_effect = ValueError("Missing OSS credentials")

        with pytest.raises(ServiceInitializationError) as exc_info:
            self.orchestrator._get_oss_uploader()

        assert "Failed to initialize OSSUploader" in str(exc_info.value)
        assert "Missing OSS credentials" in str(exc_info.value)

    @patch("app.main.create_llm_router_from_env")
    def test_llm_router_initialization_failure(self, mock_create_llm):
        """测试LLM路由器初始化失败的错误处理"""
        mock_create_llm.side_effect = ValueError("Missing LLM API keys")

        with pytest.raises(ServiceInitializationError) as exc_info:
            self.orchestrator._get_llm_router()

        assert "Failed to initialize LLMRouter" in str(exc_info.value)
        assert "Missing LLM API keys" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("app.main.ASRService")
    @patch("app.main.create_llm_router_from_env")
    async def test_url_workflow_service_integration(
        self, mock_create_llm, mock_asr_class
    ):
        """测试URL工作流中的服务集成"""
        # Setup mocks
        mock_video_info = VideoInfo(
            video_id="test123",
            platform="douyin",
            title="Test Video",
            download_url="https://example.com/video.mp4",
        )

        mock_parser = Mock()
        mock_parser.parse = AsyncMock(return_value=mock_video_info)
        self.orchestrator._url_parser = mock_parser

        mock_asr_service = Mock()
        mock_asr_service.transcribe_from_url = AsyncMock(return_value="Test transcript")
        mock_asr_class.return_value = mock_asr_service

        mock_analysis_result = AnalysisResult(
            hook="Test hook", core="Test core", cta="Test CTA"
        )
        mock_llm_router = Mock()
        mock_llm_router.analyze = AsyncMock(return_value=mock_analysis_result)
        mock_create_llm.return_value = mock_llm_router

        # Execute workflow
        result = await self.orchestrator.process_url_workflow(
            "https://example.com/share"
        )

        # Verify service calls
        mock_parser.parse.assert_called_once_with("https://example.com/share")
        mock_asr_class.assert_called_once_with()  # No OSS uploader for URL workflow
        mock_asr_service.transcribe_from_url.assert_called_once_with(
            mock_video_info.download_url
        )
        mock_llm_router.analyze.assert_called_once_with("Test transcript")

        # Verify result structure
        assert result.transcript == "Test transcript"
        assert result.analysis["video_info"]["video_id"] == "test123"
        assert result.analysis["llm_analysis"]["hook"] == "Test hook"

    @pytest.mark.asyncio
    @patch("app.main.ASRService")
    @patch("app.main.create_oss_uploader_from_env")
    @patch("app.main.create_llm_router_from_env")
    async def test_file_workflow_service_integration(
        self, mock_create_llm, mock_create_oss, mock_asr_class
    ):
        """测试文件工作流中的服务集成"""
        # Setup mocks
        mock_file_info = TempFileInfo(
            file_path=Path("/tmp/test.mp4"), original_filename="test.mp4", size=1024
        )

        mock_oss_uploader = Mock()
        mock_create_oss.return_value = mock_oss_uploader

        mock_asr_service = Mock()
        mock_asr_service.transcribe_from_file = AsyncMock(
            return_value="File transcript"
        )
        mock_asr_class.return_value = mock_asr_service

        mock_analysis_result = AnalysisResult(
            hook="File hook", core="File core", cta="File CTA"
        )
        mock_llm_router = Mock()
        mock_llm_router.analyze = AsyncMock(return_value=mock_analysis_result)
        mock_create_llm.return_value = mock_llm_router

        # Execute workflow
        result = await self.orchestrator.process_file_workflow(mock_file_info)

        # Verify service calls
        mock_create_oss.assert_called_once()
        mock_asr_class.assert_called_once_with(oss_uploader=mock_oss_uploader)
        mock_asr_service.transcribe_from_file.assert_called_once_with(
            mock_file_info.file_path
        )
        mock_llm_router.analyze.assert_called_once_with("File transcript")

        # Verify result structure
        assert result.transcript == "File transcript"
        assert result.analysis["file_info"]["original_filename"] == "test.mp4"
        assert result.analysis["llm_analysis"]["hook"] == "File hook"

    @pytest.mark.asyncio
    @patch("app.main.ASRService")
    async def test_url_workflow_asr_error_handling(self, mock_asr_class):
        """测试URL工作流中ASR服务错误处理"""
        # Setup mocks
        mock_video_info = VideoInfo(
            video_id="test123",
            platform="douyin",
            title="Test Video",
            download_url="https://example.com/video.mp4",
        )

        mock_parser = Mock()
        mock_parser.parse = AsyncMock(return_value=mock_video_info)
        self.orchestrator._url_parser = mock_parser

        mock_asr_service = Mock()
        mock_asr_service.transcribe_from_url = AsyncMock(
            side_effect=ASRError("ASR service unavailable")
        )
        mock_asr_class.return_value = mock_asr_service

        mock_llm_router = Mock()
        mock_llm_router.analyze = AsyncMock(
            return_value=AnalysisResult(
                hook="Test hook", core="Test core", cta="Test CTA"
            )
        )
        self.orchestrator._llm_router = mock_llm_router

        # Execute workflow
        result = await self.orchestrator.process_url_workflow(
            "https://example.com/share"
        )

        # Verify fallback behavior
        assert "ASR failed" in result.transcript
        assert "Test Video" in result.transcript

    @pytest.mark.asyncio
    @patch("app.main.create_oss_uploader_from_env")
    @patch("app.main.ASRService")
    async def test_file_workflow_oss_error_handling(
        self, mock_asr_class, mock_create_oss
    ):
        """测试文件工作流中OSS服务错误处理"""
        # Setup mocks
        mock_file_info = TempFileInfo(
            file_path=Path("/tmp/test.mp4"), original_filename="test.mp4", size=1024
        )

        mock_create_oss.side_effect = OSSUploaderError("OSS service unavailable")

        mock_llm_router = Mock()
        mock_llm_router.analyze = AsyncMock(
            return_value=AnalysisResult(
                hook="Test hook", core="Test core", cta="Test CTA"
            )
        )
        self.orchestrator._llm_router = mock_llm_router

        # Execute workflow
        result = await self.orchestrator.process_file_workflow(mock_file_info)

        # Verify fallback behavior
        assert "Processing failed" in result.transcript
        assert "test.mp4" in result.transcript

    @pytest.mark.asyncio
    @patch("app.main.create_llm_router_from_env")
    async def test_llm_router_error_handling(self, mock_create_llm):
        """测试LLM路由器错误处理"""
        # Setup mocks
        mock_video_info = VideoInfo(
            video_id="test123",
            platform="douyin",
            title="Test Video",
            download_url="https://example.com/video.mp4",
        )

        mock_parser = Mock()
        mock_parser.parse = AsyncMock(return_value=mock_video_info)
        self.orchestrator._url_parser = mock_parser

        mock_llm_router = Mock()
        mock_llm_router.analyze = AsyncMock(
            side_effect=LLMError("All LLM services failed")
        )
        mock_create_llm.return_value = mock_llm_router

        # Execute workflow
        result = await self.orchestrator.process_url_workflow(
            "https://example.com/share"
        )

        # Verify error handling
        assert "error" in result.analysis["llm_analysis"]
        assert "LLM analysis failed" in result.analysis["llm_analysis"]["error"]


class TestServiceInitializationErrorHandling:
    """Test service initialization error handling in error_handling module"""

    def test_service_initialization_error_mapping(self):
        """测试ServiceInitializationError的错误映射"""
        from app.error_handling import ErrorHandler, ErrorMapping

        error = ServiceInitializationError("Test initialization error")
        http_exception = ErrorHandler.create_error_response(error, time.time())

        assert http_exception.status_code == 500
        assert (
            http_exception.detail["code"] == ErrorMapping.SERVICE_INITIALIZATION_ERROR
        )
        assert http_exception.detail["success"] is False
        assert http_exception.detail["message"] == "Service initialization failed"
        assert http_exception.detail["processing_time"] is not None
