"""
Integration tests for error handling with actual service exceptions
"""

from unittest.mock import MagicMock, patch

import pytest

from .error_handling import handle_service_exception
from .services.asr_service import ASRError, ASRService
from .services.file_handler import FileHandler, FileHandlerError
from .services.llm_service import DeepSeekAdapter, LLMError
from .services.oss_uploader import OSSUploader, OSSUploaderError
from .services.url_parser import ShareURLParser, URLParserError


class TestServiceErrorIntegration:
    """Test error handling integration with actual service exceptions"""

    def test_url_parser_error_integration(self):
        """Test URLParserError handling in real scenario"""
        parser = ShareURLParser()

        # This should raise URLParserError for invalid URL
        with pytest.raises(URLParserError):
            parser._extract_url_from_text("No URL here")

        # Test error handling
        try:
            parser._extract_url_from_text("No URL here")
        except URLParserError as e:
            http_exception = handle_service_exception(e)
            assert http_exception.status_code == 400
            assert http_exception.detail["code"] == 4001

    def test_asr_service_error_integration(self):
        """Test ASRError handling in real scenario"""
        # Create ASR service with invalid API key to trigger error
        with pytest.raises(ValueError, match="DASHSCOPE_API_KEY"):
            ASRService(api_key="")

        # Test with mock to simulate ASR error
        with patch.dict("os.environ", {"DASHSCOPE_API_KEY": "test_key"}):
            asr_service = ASRService()

            # Mock dashscope to raise an error
            with patch("dashscope.audio.asr.Transcription.async_call") as mock_call:
                mock_call.side_effect = Exception("API error")

                with pytest.raises(ASRError):
                    import asyncio

                    asyncio.run(
                        asr_service.transcribe_from_url("http://example.com/video.mp4")
                    )

    def test_llm_service_error_integration(self):
        """Test LLMError handling in real scenario"""
        # Test with invalid API key
        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
            DeepSeekAdapter(api_key="")

        # Test error handling
        try:
            DeepSeekAdapter(api_key="")
        except ValueError as e:
            # Convert to LLMError for testing
            llm_error = LLMError(str(e))
            http_exception = handle_service_exception(llm_error)
            assert http_exception.status_code == 502
            assert http_exception.detail["code"] == 5002

    def test_file_handler_error_integration(self):
        """Test FileHandlerError handling in real scenario"""
        file_handler = FileHandler()

        # Create a mock UploadFile that will cause an error
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        mock_file.read.side_effect = Exception("Read error")

        # Test error handling
        import asyncio

        with pytest.raises(FileHandlerError):
            asyncio.run(file_handler.save_upload_file(mock_file))

        # Test error response
        try:
            asyncio.run(file_handler.save_upload_file(mock_file))
        except FileHandlerError as e:
            http_exception = handle_service_exception(e)
            assert http_exception.status_code == 500
            assert http_exception.detail["code"] == 5003

    def test_oss_uploader_error_integration(self):
        """Test OSSUploaderError handling in real scenario"""
        # Create OSS uploader with invalid credentials
        oss_uploader = OSSUploader(
            access_key_id="invalid",
            access_key_secret="invalid",
            endpoint="https://oss-cn-beijing.aliyuncs.com",
            bucket_name="test-bucket",
        )

        # Mock Path object
        mock_path = MagicMock()
        mock_path.name = "test.mp4"

        # This should raise OSSUploaderError due to invalid credentials
        with pytest.raises(OSSUploaderError):
            oss_uploader.upload_file(mock_path)

        # Test error handling
        try:
            oss_uploader.upload_file(mock_path)
        except OSSUploaderError as e:
            http_exception = handle_service_exception(e)
            assert http_exception.status_code == 503
            assert http_exception.detail["code"] == 5004

    def test_error_mapping_completeness(self):
        """Test that all service exceptions are properly mapped"""
        # Test all defined service exceptions
        exceptions_to_test = [
            (URLParserError("test"), 400, 4001),
            (ASRError("test"), 503, 5001),
            (LLMError("test"), 502, 5002),
            (FileHandlerError("test"), 500, 5003),
            (OSSUploaderError("test"), 503, 5004),
            (Exception("test"), 500, 9999),  # Unknown exception
        ]

        for exception, expected_http, expected_code in exceptions_to_test:
            http_exception = handle_service_exception(exception)
            assert http_exception.status_code == expected_http
            assert http_exception.detail["code"] == expected_code
            assert http_exception.detail["success"] is False
            assert http_exception.detail["data"] is None
            assert isinstance(http_exception.detail["message"], str)


if __name__ == "__main__":
    pytest.main([__file__])
