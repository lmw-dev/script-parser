# Standardized Error Handling Guide

## Overview

The ScriptParser API implements a standardized error handling mechanism that provides consistent error responses across all endpoints. This system maps service exceptions to appropriate HTTP status codes and business error codes.

## Error Response Format

All error responses follow this standardized format:

```json
{
  "code": 5001,
  "success": false,
  "data": null,
  "message": "ASR service is temporarily unavailable",
  "processing_time": 12.34
}
```

## Error Code Mapping

### Success Code
- **0**: Success - Operation completed successfully

### Client Error Codes (4xxx)
- **4001**: URL Parser Error - Failed to parse video URL
- **4002**: Validation Error - Request format or validation issues

### Server Error Codes (5xxx)
- **5001**: ASR Error - ASR service is temporarily unavailable
- **5002**: LLM Error - LLM service error occurred
- **5003**: File Handler Error - File processing error
- **5004**: OSS Uploader Error - OSS service is temporarily unavailable
- **9999**: Unknown Error - An internal server error occurred

## HTTP Status Code Mapping

| Business Code | HTTP Status | Exception Type | Description |
|---------------|-------------|----------------|-------------|
| 0 | 200 | - | Success |
| 4001 | 400 | URLParserError | Bad Request - Invalid URL |
| 4002 | 422 | ValidationError | Unprocessable Entity - Invalid input |
| 5001 | 503 | ASRError | Service Unavailable - ASR service down |
| 5002 | 502 | LLMError | Bad Gateway - LLM service error |
| 5003 | 500 | FileHandlerError | Internal Server Error - File processing |
| 5004 | 503 | OSSUploaderError | Service Unavailable - OSS service down |
| 9999 | 500 | Exception | Internal Server Error - Unknown error |

## Usage Examples

### Using the Error Handler

```python
from app.error_handling import ErrorHandler, handle_service_exception
from app.services.url_parser import URLParserError

# In your endpoint
try:
    # Service operation that might fail
    result = await some_service.process()
except URLParserError as e:
    # This will create HTTP 400 with business code 4001
    raise handle_service_exception(e, start_time)
```

### Creating Custom Error Responses

```python
from app.error_handling import ErrorHandler

# Create validation error
http_exception = ErrorHandler.create_validation_error(
    "Invalid request format", 
    start_time
)

# Create success response
success_response = ErrorHandler.create_success_response(
    data={"result": "success"},
    message="Operation completed",
    start_time=start_time
)
```

### Convenience Functions

```python
from app.error_handling import (
    create_json_decode_error,
    create_missing_input_error,
    create_form_url_error
)

# Handle common validation errors
if not valid_json:
    raise create_json_decode_error(start_time)

if not url and not file:
    raise create_missing_input_error(start_time)

if url_in_form_data:
    raise create_form_url_error(start_time)
```

## Service Exception Types

### URLParserError
- **Trigger**: Invalid URL format, unsupported platform, parsing failures
- **HTTP Status**: 400 Bad Request
- **Business Code**: 4001
- **User Message**: "Failed to parse video URL"

### ASRError
- **Trigger**: ASR service unavailable, transcription failures, API errors
- **HTTP Status**: 503 Service Unavailable
- **Business Code**: 5001
- **User Message**: "ASR service is temporarily unavailable"

### LLMError
- **Trigger**: LLM service errors, API failures, response parsing issues
- **HTTP Status**: 502 Bad Gateway
- **Business Code**: 5002
- **User Message**: "LLM service error occurred"

### FileHandlerError
- **Trigger**: File save failures, permission issues, disk space problems
- **HTTP Status**: 500 Internal Server Error
- **Business Code**: 5003
- **User Message**: "File processing error"

### OSSUploaderError
- **Trigger**: OSS upload failures, authentication issues, network problems
- **HTTP Status**: 503 Service Unavailable
- **Business Code**: 5004
- **User Message**: "OSS service is temporarily unavailable"

## Best Practices

### 1. Always Use Start Time
```python
start_time = time.time()
try:
    # Your processing logic
    pass
except Exception as e:
    raise handle_service_exception(e, start_time)
```

### 2. Handle Specific Exceptions
```python
try:
    result = await service.process()
except URLParserError as e:
    raise handle_service_exception(e, start_time)
except ASRError as e:
    raise handle_service_exception(e, start_time)
except Exception as e:
    # This will map to code 9999
    raise handle_service_exception(e, start_time)
```

### 3. Create Success Responses Consistently
```python
return ErrorHandler.create_success_response(
    data=analysis_data,
    message="Processing completed successfully",
    start_time=start_time
)
```

### 4. Log Detailed Errors
```python
import logging

logger = logging.getLogger(__name__)

try:
    result = await service.process()
except Exception as e:
    logger.error(f"Service error: {str(e)}", exc_info=True)
    raise handle_service_exception(e, start_time)
```

## Testing

The error handling system includes comprehensive tests:

- **Unit Tests**: `app/test_error_handling.py`
- **Integration Tests**: `app/test_error_integration.py`

Run tests with:
```bash
python -m pytest app/test_error_handling.py -v
python -m pytest app/test_error_integration.py -v
```

## Error Security

The error handling system follows security best practices:

1. **No Sensitive Information**: Error messages don't expose internal details
2. **Generic Messages**: User-facing messages are generic and safe
3. **Detailed Logging**: Full error details are logged server-side only
4. **Consistent Format**: All errors follow the same response structure

## Monitoring and Alerting

Business error codes can be used for monitoring:

- **4xxx codes**: Client-side issues, may indicate API usage problems
- **5xxx codes**: Server-side issues, require immediate attention
- **Code 9999**: Unknown errors, require investigation

Set up alerts based on error code patterns to proactively monitor service health.