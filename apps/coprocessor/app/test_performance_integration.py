"""
Integration tests for performance monitoring in the main application.
"""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from .main import app


class TestPerformanceMonitoringIntegration:
    """Test performance monitoring integration with the main application"""

    def test_performance_logging_in_successful_url_workflow(self, caplog):
        """Test that performance logging works in a successful URL workflow"""
        client = TestClient(app)

        # Mock all the services
        with patch("app.main.ShareURLParser") as mock_parser_class, patch(
            "app.main.ASRService"
        ) as mock_asr_class, patch(
            "app.main.create_llm_router_from_env"
        ) as mock_llm_router:
            # Setup mocks
            mock_parser = AsyncMock()
            mock_parser.parse.return_value = MagicMock(
                video_id="test123",
                platform="douyin",
                title="Test Video",
                download_url="https://example.com/video.mp4",
            )
            mock_parser_class.return_value = mock_parser

            mock_asr = AsyncMock()
            mock_asr.transcribe_from_url.return_value = "Test transcript"
            mock_asr_class.return_value = mock_asr

            mock_llm = AsyncMock()
            mock_llm.analyze.return_value = MagicMock(
                hook="Test hook", core="Test core", cta="Test CTA"
            )
            mock_llm_router.return_value = mock_llm

            # Make request
            with caplog.at_level(logging.INFO):
                response = client.post(
                    "/api/parse",
                    json={"url": "https://example.com/test-video"},
                    headers={"Content-Type": "application/json"},
                )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["success"] is True
            assert "processing_time" in data

            # Verify performance logging occurred
            log_text = caplog.text

            # Check for request ID in logs
            assert "[" in log_text and "]" in log_text  # Request ID format

            # Check for key workflow steps
            assert "Starting video_parse request" in log_text
            assert "Starting step: json_request_parsing" in log_text
            assert "Starting step: url_workflow" in log_text
            assert "Starting step: url_parsing" in log_text
            assert "Starting step: asr_transcription" in log_text
            assert "Starting step: llm_analysis" in log_text
            assert "Starting step: response_assembly" in log_text

            # Check for service calls
            assert "Service call: ShareURLParser.parse success" in log_text
            assert "Service call: ASRService.transcribe_from_url success" in log_text
            assert "Service call: LLMRouter.analyze success" in log_text

            # Check for step completions
            assert "Step json_request_parsing completed" in log_text
            assert "Step url_workflow completed" in log_text
            assert "Step response_assembly completed" in log_text

            # Check for request completion
            assert "Request completed" in log_text

    def test_performance_logging_in_error_scenario(self, caplog):
        """Test that performance logging works when errors occur"""
        client = TestClient(app)

        # Mock services with ASR failure
        with patch("app.main.ShareURLParser") as mock_parser_class, patch(
            "app.main.ASRService"
        ) as mock_asr_class:
            # Setup mocks
            mock_parser = AsyncMock()
            mock_parser.parse.return_value = MagicMock(
                video_id="test123",
                platform="douyin",
                title="Test Video",
                download_url="https://example.com/video.mp4",
            )
            mock_parser_class.return_value = mock_parser

            # ASR service fails
            from app.services.asr_service import ASRError

            mock_asr = AsyncMock()
            mock_asr.transcribe_from_url.side_effect = ASRError("ASR service failed")
            mock_asr_class.return_value = mock_asr

            # Make request
            with caplog.at_level(logging.INFO):
                response = client.post(
                    "/api/parse",
                    json={"url": "https://example.com/test-video"},
                    headers={"Content-Type": "application/json"},
                )

            # Verify response (should still succeed with fallback)
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["success"] is True

            # Verify error logging occurred
            log_text = caplog.text

            # Check for error logging
            assert "ASR transcription failed" in log_text
            assert "ASRError" in log_text

            # Check that service call failure was logged
            assert "Service call: ASRService.transcribe_from_url failure" in log_text

    def test_sensitive_data_filtering_in_requests(self, caplog):
        """Test that sensitive data is filtered from logs"""
        client = TestClient(app)

        # Mock services
        with patch("app.main.ShareURLParser") as mock_parser_class, patch(
            "app.main.ASRService"
        ) as mock_asr_class, patch(
            "app.main.create_llm_router_from_env"
        ) as mock_llm_router:
            # Setup mocks
            mock_parser = AsyncMock()
            mock_parser.parse.return_value = MagicMock(
                video_id="test123",
                platform="douyin",
                title="Test Video",
                download_url="https://example.com/video.mp4",
            )
            mock_parser_class.return_value = mock_parser

            mock_asr = AsyncMock()
            mock_asr.transcribe_from_url.return_value = "Test transcript"
            mock_asr_class.return_value = mock_asr

            mock_llm = AsyncMock()
            mock_llm.analyze.return_value = MagicMock(
                hook="Test hook", core="Test core", cta="Test CTA"
            )
            mock_llm_router.return_value = mock_llm

            # Make request with a URL that might contain sensitive info
            test_url = "https://example.com/video?token=secret123&api_key=key456"

            with caplog.at_level(logging.INFO):
                response = client.post(
                    "/api/parse",
                    json={"url": test_url},
                    headers={"Content-Type": "application/json"},
                )

            # Verify response
            assert response.status_code == 200

            # Check that the full URL with sensitive params is not in logs
            log_text = caplog.text
            assert "secret123" not in log_text
            assert "key456" not in log_text

            # But the base URL should be truncated/filtered appropriately
            assert "https://example.com/video" in log_text

    def test_request_id_uniqueness_across_requests(self, caplog):
        """Test that each request gets a unique request ID"""
        client = TestClient(app)

        # Mock services
        with patch("app.main.ShareURLParser") as mock_parser_class, patch(
            "app.main.ASRService"
        ) as mock_asr_class, patch(
            "app.main.create_llm_router_from_env"
        ) as mock_llm_router:
            # Setup mocks
            mock_parser = AsyncMock()
            mock_parser.parse.return_value = MagicMock(
                video_id="test123",
                platform="douyin",
                title="Test Video",
                download_url="https://example.com/video.mp4",
            )
            mock_parser_class.return_value = mock_parser

            mock_asr = AsyncMock()
            mock_asr.transcribe_from_url.return_value = "Test transcript"
            mock_asr_class.return_value = mock_asr

            mock_llm = AsyncMock()
            mock_llm.analyze.return_value = MagicMock(
                hook="Test hook", core="Test core", cta="Test CTA"
            )
            mock_llm_router.return_value = mock_llm

            # Make two requests
            with caplog.at_level(logging.INFO):
                response1 = client.post(
                    "/api/parse",
                    json={"url": "https://example.com/test-video-1"},
                    headers={"Content-Type": "application/json"},
                )

                response2 = client.post(
                    "/api/parse",
                    json={"url": "https://example.com/test-video-2"},
                    headers={"Content-Type": "application/json"},
                )

            # Both requests should succeed
            assert response1.status_code == 200
            assert response2.status_code == 200

            # Extract request IDs from logs
            import re

            log_text = caplog.text
            request_ids = re.findall(r"\[([a-f0-9]{8})\]", log_text)

            # Should have at least 2 different request IDs
            unique_request_ids = set(request_ids)
            assert len(unique_request_ids) >= 2

    def test_health_endpoints_performance_logging(self, caplog):
        """Test that health endpoints also have performance logging"""
        client = TestClient(app)

        with caplog.at_level(logging.INFO):
            # Test root endpoint
            response1 = client.get("/")
            assert response1.status_code == 200

            # Test health endpoint
            response2 = client.get("/health")
            assert response2.status_code == 200

        log_text = caplog.text

        # Check for health check logging
        assert "Starting health_check request" in log_text
        assert "Request completed" in log_text

        # Should have request IDs
        assert "[" in log_text and "]" in log_text
