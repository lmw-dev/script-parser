"""
Tests for the standardized error handling mechanism
"""

import time

import pytest

from .error_handling import (
    ErrorHandler,
    ErrorMapping,
    ErrorResponse,
    create_form_url_error,
    create_json_decode_error,
    create_missing_input_error,
    handle_service_exception,
)
from .services.asr_service import ASRError
from .services.file_handler import FileHandlerError
from .services.llm_service import LLMError
from .services.oss_uploader import OSSUploaderError
from .services.url_parser import URLParserError


class TestErrorMapping:
    """Test error code mapping constants"""

    def test_error_codes_defined(self):
        """Test that all required error codes are defined"""
        assert ErrorMapping.SUCCESS == 0
        assert ErrorMapping.URL_PARSER_ERROR == 4001
        assert ErrorMapping.VALIDATION_ERROR == 4002
        assert ErrorMapping.ASR_ERROR == 5001
        assert ErrorMapping.LLM_ERROR == 5002
        assert ErrorMapping.FILE_HANDLER_ERROR == 5003
        assert ErrorMapping.OSS_UPLOADER_ERROR == 5004
        assert ErrorMapping.UNKNOWN_ERROR == 9999


class TestErrorHandler:
    """Test ErrorHandler class functionality"""

    def test_url_parser_error_mapping(self):
        """Test URLParserError mapping to HTTP 400 + code 4001"""
        exception = URLParserError("Invalid URL format")
        start_time = time.time()

        http_exception = ErrorHandler.create_error_response(exception, start_time)

        assert http_exception.status_code == 400
        assert http_exception.detail["code"] == 4001
        assert http_exception.detail["success"] is False
        assert http_exception.detail["message"] == "Failed to parse video URL"
        assert http_exception.detail["data"] is None
        assert http_exception.detail["processing_time"] is not None

    def test_asr_error_mapping(self):
        """Test ASRError mapping to HTTP 503 + code 5001"""
        exception = ASRError("ASR service unavailable")
        start_time = time.time()

        http_exception = ErrorHandler.create_error_response(exception, start_time)

        assert http_exception.status_code == 503
        assert http_exception.detail["code"] == 5001
        assert http_exception.detail["success"] is False
        assert (
            http_exception.detail["message"] == "ASR service is temporarily unavailable"
        )
        assert http_exception.detail["data"] is None
        assert http_exception.detail["processing_time"] is not None

    def test_llm_error_mapping(self):
        """Test LLMError mapping to HTTP 502 + code 5002"""
        exception = LLMError("LLM service error")
        start_time = time.time()

        http_exception = ErrorHandler.create_error_response(exception, start_time)

        assert http_exception.status_code == 502
        assert http_exception.detail["code"] == 5002
        assert http_exception.detail["success"] is False
        assert http_exception.detail["message"] == "LLM service error occurred"
        assert http_exception.detail["data"] is None
        assert http_exception.detail["processing_time"] is not None

    def test_file_handler_error_mapping(self):
        """Test FileHandlerError mapping to HTTP 500 + code 5003"""
        exception = FileHandlerError("File processing failed")
        start_time = time.time()

        http_exception = ErrorHandler.create_error_response(exception, start_time)

        assert http_exception.status_code == 500
        assert http_exception.detail["code"] == 5003
        assert http_exception.detail["success"] is False
        assert http_exception.detail["message"] == "File processing error"
        assert http_exception.detail["data"] is None
        assert http_exception.detail["processing_time"] is not None

    def test_oss_uploader_error_mapping(self):
        """Test OSSUploaderError mapping to HTTP 503 + code 5004"""
        exception = OSSUploaderError("OSS upload failed")
        start_time = time.time()

        http_exception = ErrorHandler.create_error_response(exception, start_time)

        assert http_exception.status_code == 503
        assert http_exception.detail["code"] == 5004
        assert http_exception.detail["success"] is False
        assert (
            http_exception.detail["message"] == "OSS service is temporarily unavailable"
        )
        assert http_exception.detail["data"] is None
        assert http_exception.detail["processing_time"] is not None

    def test_unknown_exception_mapping(self):
        """Test unknown Exception mapping to HTTP 500 + code 9999"""
        exception = ValueError("Some unknown error")
        start_time = time.time()

        http_exception = ErrorHandler.create_error_response(exception, start_time)

        assert http_exception.status_code == 500
        assert http_exception.detail["code"] == 9999
        assert http_exception.detail["success"] is False
        assert http_exception.detail["message"] == "An internal server error occurred"
        assert http_exception.detail["data"] is None
        assert http_exception.detail["processing_time"] is not None

    def test_error_response_without_start_time(self):
        """Test error response creation without start time"""
        exception = URLParserError("Invalid URL")

        http_exception = ErrorHandler.create_error_response(exception)

        assert http_exception.status_code == 400
        assert http_exception.detail["code"] == 4001
        assert http_exception.detail["processing_time"] is None

    def test_validation_error_creation(self):
        """Test validation error creation"""
        message = "Invalid request format"
        start_time = time.time()

        http_exception = ErrorHandler.create_validation_error(message, start_time)

        assert http_exception.status_code == 422
        assert http_exception.detail["code"] == 4002
        assert http_exception.detail["success"] is False
        assert http_exception.detail["message"] == message
        assert http_exception.detail["data"] is None
        assert http_exception.detail["processing_time"] is not None

    def test_success_response_creation(self):
        """Test success response creation"""
        data = {"result": "success"}
        message = "Operation completed"
        start_time = time.time()

        response = ErrorHandler.create_success_response(data, message, start_time)

        assert response["code"] == 0
        assert response["success"] is True
        assert response["data"] == data
        assert response["message"] == message
        assert response["processing_time"] is not None


class TestConvenienceFunctions:
    """Test convenience functions for error handling"""

    def test_handle_service_exception(self):
        """Test handle_service_exception convenience function"""
        exception = ASRError("Service error")
        start_time = time.time()

        http_exception = handle_service_exception(exception, start_time)

        assert http_exception.status_code == 503
        assert http_exception.detail["code"] == 5001

    def test_create_json_decode_error(self):
        """Test JSON decode error creation"""
        start_time = time.time()

        http_exception = create_json_decode_error(start_time)

        assert http_exception.status_code == 422
        assert http_exception.detail["code"] == 4002
        assert http_exception.detail["message"] == "Invalid JSON format in request body"

    def test_create_missing_input_error(self):
        """Test missing input error creation"""
        start_time = time.time()

        http_exception = create_missing_input_error(start_time)

        assert http_exception.status_code == 400
        assert http_exception.detail["code"] == 4002
        assert http_exception.detail["message"] == "Either URL or file must be provided"

    def test_create_form_url_error(self):
        """Test form URL error creation"""
        start_time = time.time()

        http_exception = create_form_url_error(start_time)

        assert http_exception.status_code == 422
        assert http_exception.detail["code"] == 4002
        assert (
            http_exception.detail["message"]
            == "URL should be sent as JSON, not form data"
        )


class TestErrorResponse:
    """Test ErrorResponse model"""

    def test_error_response_model(self):
        """Test ErrorResponse model validation"""
        response = ErrorResponse(
            code=5001, message="Service unavailable", processing_time=1.5
        )

        assert response.code == 5001
        assert response.success is False
        assert response.data is None
        assert response.message == "Service unavailable"
        assert response.processing_time == 1.5

    def test_error_response_model_defaults(self):
        """Test ErrorResponse model with defaults"""
        response = ErrorResponse(code=4001, message="Client error")

        assert response.code == 4001
        assert response.success is False
        assert response.data is None
        assert response.message == "Client error"
        assert response.processing_time is None


if __name__ == "__main__":
    pytest.main([__file__])
