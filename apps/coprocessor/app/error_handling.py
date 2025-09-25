"""
Standardized error handling mechanism for the ScriptParser API
Provides centralized error mapping and response formatting
"""

import time
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel

from .services.asr_service import ASRError
from .services.file_handler import FileHandlerError
from .services.llm_service import LLMError
from .services.oss_uploader import OSSUploaderError
from .services.url_parser import URLParserError


class ServiceInitializationError(Exception):
    """Custom exception for service initialization failures"""

    pass


class ErrorResponse(BaseModel):
    """Standardized error response model"""

    code: int
    success: bool = False
    data: Any | None = None
    message: str
    processing_time: float | None = None


class ErrorMapping:
    """Error code mapping configuration"""

    # Success code
    SUCCESS = 0

    # Client error codes (4xxx)
    URL_PARSER_ERROR = 4001
    VALIDATION_ERROR = 4002

    # Server error codes (5xxx)
    ASR_ERROR = 5001
    LLM_ERROR = 5002
    FILE_HANDLER_ERROR = 5003
    OSS_UPLOADER_ERROR = 5004
    SERVICE_INITIALIZATION_ERROR = 5005
    UNKNOWN_ERROR = 9999


class ErrorHandler:
    """Centralized error handling and mapping"""

    # Error mapping table: Exception type -> (HTTP status code, business error code, user message)
    ERROR_MAPPINGS: dict[type, tuple[int, int, str]] = {
        URLParserError: (
            400,
            ErrorMapping.URL_PARSER_ERROR,
            "Failed to parse video URL",
        ),
        ASRError: (
            503,
            ErrorMapping.ASR_ERROR,
            "ASR service is temporarily unavailable",
        ),
        LLMError: (502, ErrorMapping.LLM_ERROR, "LLM service error occurred"),
        FileHandlerError: (
            500,
            ErrorMapping.FILE_HANDLER_ERROR,
            "File processing error",
        ),
        OSSUploaderError: (
            503,
            ErrorMapping.OSS_UPLOADER_ERROR,
            "OSS service is temporarily unavailable",
        ),
        ServiceInitializationError: (
            500,
            ErrorMapping.SERVICE_INITIALIZATION_ERROR,
            "Service initialization failed",
        ),
    }

    @classmethod
    def create_error_response(
        cls, exception: Exception, start_time: float | None = None
    ) -> HTTPException:
        """
        Create standardized error response from exception

        Args:
            exception: The exception that occurred
            start_time: Request start time for calculating processing time

        Returns:
            HTTPException with standardized error format
        """
        # Calculate processing time if start_time provided
        processing_time = None
        if start_time is not None:
            processing_time = time.time() - start_time

        # Get error mapping for the exception type
        exception_type = type(exception)
        if exception_type in cls.ERROR_MAPPINGS:
            http_status, business_code, _ = cls.ERROR_MAPPINGS[exception_type]
            user_message = str(exception)  # Use the specific exception message
        else:
            # Handle unknown exceptions
            http_status = 500
            business_code = ErrorMapping.UNKNOWN_ERROR
            user_message = "An internal server error occurred"

        # Create error response
        error_detail = {
            "code": business_code,
            "success": False,
            "data": None,
            "message": user_message,
            "processing_time": processing_time,
        }

        return HTTPException(status_code=http_status, detail=error_detail)

    @classmethod
    def create_validation_error(
        cls, message: str, start_time: float | None = None
    ) -> HTTPException:
        """
        Create validation error response

        Args:
            message: Validation error message
            start_time: Request start time for calculating processing time

        Returns:
            HTTPException with validation error format
        """
        processing_time = None
        if start_time is not None:
            processing_time = time.time() - start_time

        error_detail = {
            "code": ErrorMapping.VALIDATION_ERROR,
            "success": False,
            "data": None,
            "message": message,
            "processing_time": processing_time,
        }

        return HTTPException(status_code=422, detail=error_detail)

    @classmethod
    def create_success_response(
        cls,
        data: Any,
        message: str = "Processing completed successfully",
        start_time: float | None = None,
    ) -> dict[str, Any]:
        """
        Create standardized success response

        Args:
            data: Response data
            message: Success message
            start_time: Request start time for calculating processing time

        Returns:
            Standardized success response dictionary
        """
        processing_time = None
        if start_time is not None:
            processing_time = time.time() - start_time

        return {
            "code": ErrorMapping.SUCCESS,
            "success": True,
            "data": data,
            "message": message,
            "processing_time": processing_time,
        }


def handle_service_exception(
    exception: Exception, start_time: float | None = None
) -> HTTPException:
    """
    Convenience function to handle service exceptions

    Args:
        exception: The exception that occurred
        start_time: Request start time for calculating processing time

    Returns:
        HTTPException with standardized error format
    """
    return ErrorHandler.create_error_response(exception, start_time)


def create_json_decode_error(start_time: float | None = None) -> HTTPException:
    """
    Create JSON decode error response

    Args:
        start_time: Request start time for calculating processing time

    Returns:
        HTTPException for JSON decode errors
    """
    return ErrorHandler.create_validation_error(
        "Invalid JSON format in request body", start_time
    )


def create_missing_input_error(start_time: float | None = None) -> HTTPException:
    """
    Create missing input error response

    Args:
        start_time: Request start time for calculating processing time

    Returns:
        HTTPException for missing input errors
    """
    processing_time = None
    if start_time is not None:
        processing_time = time.time() - start_time

    error_detail = {
        "code": ErrorMapping.VALIDATION_ERROR,
        "success": False,
        "data": None,
        "message": "Either URL or file must be provided",
        "processing_time": processing_time,
    }

    return HTTPException(status_code=400, detail=error_detail)


def create_form_url_error(start_time: float | None = None) -> HTTPException:
    """
    Create form URL error response

    Args:
        start_time: Request start time for calculating processing time

    Returns:
        HTTPException for form URL errors
    """
    return ErrorHandler.create_validation_error(
        "URL should be sent as JSON, not form data", start_time
    )
