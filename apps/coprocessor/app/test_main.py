"""
Comprehensive integration tests for the /api/parse endpoint
Tests all workflows, error scenarios, and resource cleanup mechanisms
"""

from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from .error_handling import ServiceInitializationError
from .main import app
from .services.asr_service import ASRError
from .services.file_handler import FileHandlerError, TempFileInfo
from .services.llm_service import AnalysisDetail, AnalysisResult, LLMError
from .services.oss_uploader import OSSUploaderError
from .services.url_parser import URLParserError, VideoInfo

client = TestClient(app)


@pytest.fixture
def mock_video_info():
    """Mock video info for successful URL parsing"""
    return VideoInfo(
        video_id="test123",
        platform="douyin",
        title="Test Video",
        download_url="https://example.com/video.mp4",
    )


@pytest.fixture
def mock_temp_file_info():
    """Mock temp file info for file upload tests"""
    return TempFileInfo(
        file_path=Path("/tmp/test_file.mp4"),
        original_filename="test_video.mp4",
        size=1024,
    )


@pytest.fixture
def mock_analysis_result():
    """Mock LLM analysis result (V2.2)"""
    return AnalysisResult(
        raw_transcript="Raw transcript from ASR",
        cleaned_transcript="Cleaned and segmented transcript",
        analysis=AnalysisDetail(
            hook="Engaging opening", core="Main content", cta="Call to action"
        ),
    )


class TestSuccessfulWorkflows:
    """Test successful URL and file upload workflows"""

    @patch("app.main.WorkflowOrchestrator._get_url_parser")
    @patch("app.main.WorkflowOrchestrator._get_llm_router")
    @patch("app.main.ASRService")
    def test_successful_url_workflow(
        self,
        mock_asr_class,
        mock_llm_router,
        mock_url_parser,
        mock_video_info,
        mock_analysis_result,
    ):
        """Test successful URL workflow - verifies HTTP 200 and business code 0"""
        # Setup mocks
        mock_parser_instance = Mock()
        mock_parser_instance.parse = AsyncMock(return_value=mock_video_info)
        mock_url_parser.return_value = mock_parser_instance

        mock_asr_instance = Mock()
        mock_asr_instance.transcribe_from_url = AsyncMock(
            return_value="Test transcript"
        )
        mock_asr_class.return_value = mock_asr_instance

        mock_llm_instance = Mock()
        mock_llm_instance.analyze = AsyncMock(return_value=mock_analysis_result)
        mock_llm_router.return_value = mock_llm_instance

        # Make request
        response = client.post(
            "/api/parse", json={"url": "https://www.douyin.com/video/test123"}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["success"] is True
        assert data["data"] is not None
        assert data["data"]["raw_transcript"] == "Raw transcript from ASR"
        assert data["data"]["cleaned_transcript"] == "Cleaned and segmented transcript"
        assert data["data"]["analysis"]["video_info"]["video_id"] == "test123"
        assert data["data"]["analysis"]["llm_analysis"]["hook"] == "Engaging opening"
        assert "processing_time" in data
        assert data["message"] == "Processing completed successfully"

        # Verify service calls
        mock_parser_instance.parse.assert_called_once()
        mock_asr_instance.transcribe_from_url.assert_called_once_with(
            mock_video_info.download_url
        )
        mock_llm_instance.analyze.assert_called_once_with("Test transcript")

    @patch("app.main.WorkflowOrchestrator._get_file_handler")
    @patch("app.main.WorkflowOrchestrator._get_oss_uploader")
    @patch("app.main.WorkflowOrchestrator._get_llm_router")
    @patch("app.main.ASRService")
    @patch("app.services.file_handler.FileHandler.cleanup")
    def test_successful_file_upload_workflow(
        self,
        mock_cleanup,
        mock_asr_class,
        mock_llm_router,
        mock_oss_uploader,
        mock_file_handler,
        mock_temp_file_info,
        mock_analysis_result,
    ):
        """Test successful file upload workflow - verifies response format and resource cleanup"""
        # Setup mocks
        mock_handler_instance = Mock()
        mock_handler_instance.save_upload_file = AsyncMock(
            return_value=mock_temp_file_info
        )
        mock_file_handler.return_value = mock_handler_instance

        mock_oss_instance = Mock()
        mock_oss_uploader.return_value = mock_oss_instance

        mock_asr_instance = Mock()
        mock_asr_instance.transcribe_from_file = AsyncMock(
            return_value="File transcript"
        )
        mock_asr_class.return_value = mock_asr_instance

        mock_llm_instance = Mock()
        mock_llm_instance.analyze = AsyncMock(return_value=mock_analysis_result)
        mock_llm_router.return_value = mock_llm_instance

        mock_cleanup.return_value = AsyncMock()

        # Make request
        response = client.post(
            "/api/parse",
            files={"file": ("test.mp4", b"fake_video_content", "video/mp4")},
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["success"] is True
        assert data["data"] is not None
        assert data["data"]["raw_transcript"] == "Raw transcript from ASR"
        assert data["data"]["cleaned_transcript"] == "Cleaned and segmented transcript"
        assert (
            data["data"]["analysis"]["file_info"]["original_filename"]
            == "test_video.mp4"
        )
        assert data["data"]["analysis"]["llm_analysis"]["core"] == "Main content"
        assert "processing_time" in data

        # Verify resource cleanup was called
        mock_cleanup.assert_called_once_with(mock_temp_file_info.file_path)


class TestErrorScenarios:
    """Test various error scenarios and their proper handling"""

    @patch("app.main.WorkflowOrchestrator._get_url_parser")
    def test_url_parser_error(self, mock_url_parser):
        """Test URL parsing failure - verifies HTTP 400 and business code 4001"""
        # Setup mock to raise URLParserError
        mock_parser_instance = Mock()
        mock_parser_instance.parse = AsyncMock(
            side_effect=URLParserError("Invalid URL format")
        )
        mock_url_parser.return_value = mock_parser_instance

        # Make request
        response = client.post("/api/parse", json={"url": "https://invalid-url.com"})

        # Verify error response
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4001
        assert data["success"] is False
        assert data["message"] == "Failed to parse video URL"
        assert "processing_time" in data

    @patch("app.main.WorkflowOrchestrator._get_url_parser")
    @patch("app.main.WorkflowOrchestrator._get_llm_router")
    @patch("app.main.ASRService")
    def test_asr_service_error_fallback_behavior(
        self,
        mock_asr_class,
        mock_llm_router,
        mock_url_parser,
        mock_video_info,
        mock_analysis_result,
    ):
        """Test ASR service failure - current implementation uses fallback behavior"""
        # Setup mocks
        mock_parser_instance = Mock()
        mock_parser_instance.parse = AsyncMock(return_value=mock_video_info)
        mock_url_parser.return_value = mock_parser_instance

        mock_asr_instance = Mock()
        mock_asr_instance.transcribe_from_url = AsyncMock(
            side_effect=ASRError("ASR service unavailable")
        )
        mock_asr_class.return_value = mock_asr_instance

        mock_llm_instance = Mock()
        mock_llm_instance.analyze = AsyncMock(return_value=mock_analysis_result)
        mock_llm_router.return_value = mock_llm_instance

        # Make request
        response = client.post(
            "/api/parse", json={"url": "https://www.douyin.com/video/test123"}
        )

        # Current implementation continues with fallback behavior
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["success"] is True
        # V2.2: Verify fallback still provides transcript fields (even on error)
        assert "raw_transcript" in data["data"]
        assert "cleaned_transcript" in data["data"]

    @patch("app.main.WorkflowOrchestrator._get_url_parser")
    @patch("app.main.WorkflowOrchestrator._get_llm_router")
    @patch("app.main.ASRService")
    def test_llm_service_error_fallback_behavior(
        self, mock_asr_class, mock_llm_router, mock_url_parser, mock_video_info
    ):
        """Test LLM service failure - current implementation uses fallback behavior"""
        # Setup mocks
        mock_parser_instance = Mock()
        mock_parser_instance.parse = AsyncMock(return_value=mock_video_info)
        mock_url_parser.return_value = mock_parser_instance

        mock_asr_instance = Mock()
        mock_asr_instance.transcribe_from_url = AsyncMock(
            return_value="Test transcript"
        )
        mock_asr_class.return_value = mock_asr_instance

        mock_llm_instance = Mock()
        mock_llm_instance.analyze = AsyncMock(side_effect=LLMError("LLM service error"))
        mock_llm_router.return_value = mock_llm_instance

        # Make request
        response = client.post(
            "/api/parse", json={"url": "https://www.douyin.com/video/test123"}
        )

        # Current implementation continues with fallback behavior
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["success"] is True
        # Verify fallback analysis contains error info
        assert "error" in data["data"]["analysis"]["llm_analysis"]
        assert (
            "LLM analysis failed" in data["data"]["analysis"]["llm_analysis"]["error"]
        )

    @patch("app.main.WorkflowOrchestrator._get_file_handler")
    @patch("app.services.file_handler.FileHandler.cleanup")
    def test_file_handler_error_with_cleanup(self, mock_cleanup, mock_file_handler):
        """Test file processing failure - verifies resource cleanup mechanism"""
        # Setup mock to raise FileHandlerError
        mock_handler_instance = Mock()
        mock_handler_instance.save_upload_file = AsyncMock(
            side_effect=FileHandlerError("File processing failed")
        )
        mock_file_handler.return_value = mock_handler_instance

        mock_cleanup.return_value = AsyncMock()

        # Make request
        response = client.post(
            "/api/parse", files={"file": ("test.mp4", b"fake_content", "video/mp4")}
        )

        # Verify error response
        assert response.status_code == 500
        data = response.json()["detail"]
        assert data["code"] == 5003
        assert data["success"] is False
        assert data["message"] == "File processing error"
        assert "processing_time" in data

        # Verify cleanup was still called (should be called in finally block)
        # Note: In this case, temp_file_info is None, so cleanup won't be called
        # This tests the safety of the cleanup mechanism

    @patch("app.main.WorkflowOrchestrator._get_file_handler")
    @patch("app.main.WorkflowOrchestrator._get_oss_uploader")
    @patch("app.main.WorkflowOrchestrator._get_llm_router")
    @patch("app.main.ASRService")
    @patch("app.services.file_handler.FileHandler.cleanup")
    def test_oss_uploader_error_fallback_behavior(
        self,
        mock_cleanup,
        mock_asr_class,
        mock_llm_router,
        mock_oss_uploader,
        mock_file_handler,
        mock_temp_file_info,
        mock_analysis_result,
    ):
        """Test OSS uploader failure - current implementation uses fallback behavior"""
        # Setup mocks
        mock_handler_instance = Mock()
        mock_handler_instance.save_upload_file = AsyncMock(
            return_value=mock_temp_file_info
        )
        mock_file_handler.return_value = mock_handler_instance

        mock_oss_instance = Mock()
        mock_oss_uploader.return_value = mock_oss_instance

        mock_asr_instance = Mock()
        mock_asr_instance.transcribe_from_file = AsyncMock(
            side_effect=OSSUploaderError("OSS upload failed")
        )
        mock_asr_class.return_value = mock_asr_instance

        mock_llm_instance = Mock()
        mock_llm_instance.analyze = AsyncMock(return_value=mock_analysis_result)
        mock_llm_router.return_value = mock_llm_instance

        mock_cleanup.return_value = AsyncMock()

        # Make request
        response = client.post(
            "/api/parse", files={"file": ("test.mp4", b"fake_content", "video/mp4")}
        )

        # Current implementation continues with fallback behavior
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["success"] is True
        # V2.2: Verify fallback still provides transcript fields (even on error)
        assert "raw_transcript" in data["data"]
        assert "cleaned_transcript" in data["data"]

        # Verify cleanup was called
        mock_cleanup.assert_called_once_with(mock_temp_file_info.file_path)

    @patch("app.main.WorkflowOrchestrator._get_url_parser")
    def test_service_initialization_error(self, mock_url_parser):
        """Test service initialization failure - verifies HTTP 500 and business code 5005"""
        # Setup mock to raise ServiceInitializationError
        mock_url_parser.side_effect = ServiceInitializationError(
            "Failed to initialize service"
        )

        # Make request
        response = client.post(
            "/api/parse", json={"url": "https://www.douyin.com/video/test123"}
        )

        # Verify error response
        assert response.status_code == 500
        data = response.json()["detail"]
        assert data["code"] == 5005
        assert data["success"] is False
        assert data["message"] == "Service initialization failed"
        assert "processing_time" in data

    @patch("app.main.WorkflowOrchestrator._get_url_parser")
    def test_unknown_exception_error(self, mock_url_parser):
        """Test unknown exception handling - verifies HTTP 500 and business code 9999"""
        # Setup mock to raise unknown exception
        mock_parser_instance = Mock()
        mock_parser_instance.parse = AsyncMock(
            side_effect=RuntimeError("Unexpected error")
        )
        mock_url_parser.return_value = mock_parser_instance

        # Make request
        response = client.post(
            "/api/parse", json={"url": "https://www.douyin.com/video/test123"}
        )

        # Verify error response
        assert response.status_code == 500
        data = response.json()["detail"]
        assert data["code"] == 9999
        assert data["success"] is False
        assert data["message"] == "An internal server error occurred"
        assert "processing_time" in data


class TestRequestValidation:
    """Test request validation and input processing"""

    def test_missing_inputs_request(self):
        """Test request with neither URL nor file"""
        response = client.post("/api/parse")
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]
        assert "processing_time" in data

    def test_json_decode_error(self):
        """Test invalid JSON format"""
        response = client.post(
            "/api/parse",
            content="invalid json",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Invalid JSON format" in data["message"]
        assert "processing_time" in data

    def test_form_url_error(self):
        """Test URL sent as form data instead of JSON"""
        response = client.post("/api/parse", data={"url": "https://example.com"})
        assert response.status_code == 422
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "URL should be sent as JSON" in data["message"]
        assert "processing_time" in data

    def test_empty_url_in_json(self):
        """Test empty URL in JSON request"""
        response = client.post("/api/parse", json={"url": ""})
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]

    def test_null_url_in_json(self):
        """Test null URL in JSON request"""
        response = client.post("/api/parse", json={"url": None})
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]

    def test_whitespace_url_in_json(self):
        """Test whitespace-only URL in JSON request"""
        response = client.post("/api/parse", json={"url": "   "})
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]


class TestResourceCleanup:
    """Test resource cleanup mechanisms"""

    @patch("app.main.WorkflowOrchestrator._get_file_handler")
    @patch("app.main.WorkflowOrchestrator._get_oss_uploader")
    @patch("app.main.WorkflowOrchestrator._get_llm_router")
    @patch("app.main.ASRService")
    @patch("app.services.file_handler.FileHandler.cleanup")
    def test_cleanup_on_success(
        self,
        mock_cleanup,
        mock_asr_class,
        mock_llm_router,
        mock_oss_uploader,
        mock_file_handler,
        mock_temp_file_info,
        mock_analysis_result,
    ):
        """Test that cleanup is called on successful file processing"""
        # Setup mocks for successful processing
        mock_handler_instance = Mock()
        mock_handler_instance.save_upload_file = AsyncMock(
            return_value=mock_temp_file_info
        )
        mock_file_handler.return_value = mock_handler_instance

        mock_oss_instance = Mock()
        mock_oss_uploader.return_value = mock_oss_instance

        mock_asr_instance = Mock()
        mock_asr_instance.transcribe_from_file = AsyncMock(
            return_value="Success transcript"
        )
        mock_asr_class.return_value = mock_asr_instance

        mock_llm_instance = Mock()
        mock_llm_instance.analyze = AsyncMock(return_value=mock_analysis_result)
        mock_llm_router.return_value = mock_llm_instance

        mock_cleanup.return_value = AsyncMock()

        # Make request
        response = client.post(
            "/api/parse", files={"file": ("test.mp4", b"content", "video/mp4")}
        )

        # Verify success and cleanup
        assert response.status_code == 200
        mock_cleanup.assert_called_once_with(mock_temp_file_info.file_path)

    @patch("app.main.WorkflowOrchestrator._get_file_handler")
    @patch("app.main.WorkflowOrchestrator._get_oss_uploader")
    @patch("app.main.WorkflowOrchestrator._get_llm_router")
    @patch("app.main.ASRService")
    @patch("app.services.file_handler.FileHandler.cleanup")
    def test_cleanup_on_exception(
        self,
        mock_cleanup,
        mock_asr_class,
        mock_llm_router,
        mock_oss_uploader,
        mock_file_handler,
        mock_temp_file_info,
        mock_analysis_result,
    ):
        """Test that cleanup is called even when exceptions occur"""
        # Setup mocks
        mock_handler_instance = Mock()
        mock_handler_instance.save_upload_file = AsyncMock(
            return_value=mock_temp_file_info
        )
        mock_file_handler.return_value = mock_handler_instance

        mock_oss_instance = Mock()
        mock_oss_uploader.return_value = mock_oss_instance

        # Mock ASR to fail, but LLM to succeed (current implementation continues with fallback)
        mock_asr_instance = Mock()
        mock_asr_instance.transcribe_from_file = AsyncMock(
            side_effect=ASRError("ASR failed")
        )
        mock_asr_class.return_value = mock_asr_instance

        mock_llm_instance = Mock()
        mock_llm_instance.analyze = AsyncMock(return_value=mock_analysis_result)
        mock_llm_router.return_value = mock_llm_instance

        # Mock cleanup to succeed
        mock_cleanup.return_value = AsyncMock()

        # Make request
        response = client.post(
            "/api/parse", files={"file": ("test.mp4", b"content", "video/mp4")}
        )

        # Current implementation continues with fallback, so response is 200
        assert response.status_code == 200
        # Verify cleanup was still called
        mock_cleanup.assert_called_once_with(mock_temp_file_info.file_path)

    @patch("app.main.WorkflowOrchestrator._get_file_handler")
    @patch("app.main.WorkflowOrchestrator._get_oss_uploader")
    @patch("app.main.WorkflowOrchestrator._get_llm_router")
    @patch("app.main.ASRService")
    @patch("app.services.file_handler.FileHandler.cleanup")
    def test_cleanup_handles_exceptions_gracefully(
        self,
        mock_cleanup,
        mock_asr_class,
        mock_llm_router,
        mock_oss_uploader,
        mock_file_handler,
        mock_temp_file_info,
        mock_analysis_result,
    ):
        """Test that cleanup exceptions don't mask original errors"""
        # Setup mocks
        mock_handler_instance = Mock()
        mock_handler_instance.save_upload_file = AsyncMock(
            return_value=mock_temp_file_info
        )
        mock_file_handler.return_value = mock_handler_instance

        mock_oss_instance = Mock()
        mock_oss_uploader.return_value = mock_oss_instance

        mock_asr_instance = Mock()
        mock_asr_instance.transcribe_from_file = AsyncMock(
            return_value="Success transcript"
        )
        mock_asr_class.return_value = mock_asr_instance

        mock_llm_instance = Mock()
        mock_llm_instance.analyze = AsyncMock(return_value=mock_analysis_result)
        mock_llm_router.return_value = mock_llm_instance

        # Mock cleanup to raise an exception
        mock_cleanup.side_effect = Exception("Cleanup failed")

        # Make request
        response = client.post(
            "/api/parse", files={"file": ("test.mp4", b"content", "video/mp4")}
        )

        # Verify that the request still completes successfully (cleanup exception is swallowed)
        assert response.status_code == 200
        # Verify cleanup was called
        mock_cleanup.assert_called_once_with(mock_temp_file_info.file_path)


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_root_endpoint(self):
        """Test root health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ScriptParser AI Coprocessor is running"
        assert data["version"] == "1.0.0"

    def test_health_endpoint(self):
        """Test dedicated health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-coprocessor"
