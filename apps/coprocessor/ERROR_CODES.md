# ScriptParser API Error Codes Reference

## Overview

The ScriptParser API uses a dual error code system:
- **HTTP Status Codes**: Standard HTTP status codes for client/server error classification
- **Business Error Codes**: Application-specific codes for detailed error identification

All error responses follow this format:
```json
{
  "code": 4001,
  "success": false,
  "data": null,
  "message": "User-friendly error message",
  "processing_time": 12.34
}
```

## Success Code

| Business Code | HTTP Status | Description |
|---------------|-------------|-------------|
| 0 | 200 | Success - Request processed successfully |

## Client Error Codes (4xxx)

### 4001 - URL Parser Error
- **HTTP Status**: 400 Bad Request
- **Cause**: Invalid or unsupported video URL
- **User Message**: "Failed to parse video URL"
- **Common Scenarios**:
  - Malformed URL format
  - Unsupported video platform
  - Private or deleted video
  - Network timeout during URL parsing

**Example Response**:
```json
{
  "code": 4001,
  "success": false,
  "data": null,
  "message": "Failed to parse video URL",
  "processing_time": 2.15
}
```

**Troubleshooting**:
- Verify the URL is accessible in a browser
- Check if the platform is supported (Douyin, Xiaohongshu)
- Ensure the URL is not private or region-restricted

### 4002 - Validation Error
- **HTTP Status**: 400 Bad Request or 422 Unprocessable Entity
- **Cause**: Request format or validation issues
- **User Messages**:
  - "Either URL or file must be provided"
  - "Invalid JSON format in request body"
  - "URL should be sent as JSON, not form data"

**Common Scenarios**:

#### Missing Input (HTTP 400)
```json
{
  "code": 4002,
  "success": false,
  "data": null,
  "message": "Either URL or file must be provided",
  "processing_time": 0.05
}
```

#### Invalid JSON (HTTP 422)
```json
{
  "code": 4002,
  "success": false,
  "data": null,
  "message": "Invalid JSON format in request body",
  "processing_time": 0.12
}
```

#### Form Data URL Error (HTTP 422)
```json
{
  "code": 4002,
  "success": false,
  "data": null,
  "message": "URL should be sent as JSON, not form data",
  "processing_time": 0.08
}
```

**Troubleshooting**:
- For URL requests: Use `Content-Type: application/json` and send `{"url": "..."}`
- For file uploads: Use `Content-Type: multipart/form-data` with file field
- Validate JSON syntax before sending

## Server Error Codes (5xxx)

### 5001 - ASR Service Error
- **HTTP Status**: 503 Service Unavailable
- **Cause**: Audio transcription service issues
- **User Message**: "ASR service is temporarily unavailable"
- **Common Scenarios**:
  - DashScope API service downtime
  - API quota exceeded
  - Network connectivity issues
  - Audio format not supported
  - File too large for ASR processing

**Example Response**:
```json
{
  "code": 5001,
  "success": false,
  "data": null,
  "message": "ASR service is temporarily unavailable",
  "processing_time": 25.67
}
```

**Troubleshooting**:
- Check DashScope service status
- Verify `DASHSCOPE_API_KEY` environment variable
- Ensure audio file is in supported format
- Check file size limits (max 100MB)

### 5002 - LLM Service Error
- **HTTP Status**: 502 Bad Gateway
- **Cause**: Language model service issues
- **User Message**: "LLM service error occurred"
- **Common Scenarios**:
  - DeepSeek API service issues
  - Kimi API fallback failure
  - API rate limiting
  - Invalid API responses
  - Network timeout

**Example Response**:
```json
{
  "code": 5002,
  "success": false,
  "data": null,
  "message": "LLM service error occurred",
  "processing_time": 18.45
}
```

**Troubleshooting**:
- Verify `DEEPSEEK_API_KEY` and `KIMI_API_KEY` environment variables
- Check API service status for both providers
- Review API usage quotas
- Ensure network connectivity to LLM services

### 5003 - File Handler Error
- **HTTP Status**: 500 Internal Server Error
- **Cause**: File processing and storage issues
- **User Message**: "File processing error"
- **Common Scenarios**:
  - Disk space insufficient
  - File permission errors
  - Corrupted file upload
  - File size exceeds limits
  - Temporary directory issues

**Example Response**:
```json
{
  "code": 5003,
  "success": false,
  "data": null,
  "message": "File processing error",
  "processing_time": 5.23
}
```

**Troubleshooting**:
- Check available disk space
- Verify file upload integrity
- Ensure file size is under 100MB limit
- Check temporary directory permissions

### 5004 - OSS Service Error
- **HTTP Status**: 503 Service Unavailable
- **Cause**: Object Storage Service issues
- **User Message**: "OSS service is temporarily unavailable"
- **Common Scenarios**:
  - Alibaba Cloud OSS service downtime
  - Invalid OSS credentials
  - Bucket access permission issues
  - Network connectivity to OSS
  - Storage quota exceeded

**Example Response**:
```json
{
  "code": 5004,
  "success": false,
  "data": null,
  "message": "OSS service is temporarily unavailable",
  "processing_time": 8.91
}
```

**Troubleshooting**:
- Verify OSS credentials in environment variables
- Check bucket permissions and existence
- Ensure network connectivity to OSS endpoints
- Review storage quota and billing status

### 5005 - Service Initialization Error
- **HTTP Status**: 500 Internal Server Error
- **Cause**: Internal service configuration issues
- **User Message**: "Service initialization failed"
- **Common Scenarios**:
  - Missing required environment variables
  - Invalid service configurations
  - Dependency initialization failures
  - Resource allocation issues

**Example Response**:
```json
{
  "code": 5005,
  "success": false,
  "data": null,
  "message": "Service initialization failed",
  "processing_time": 0.15
}
```

**Troubleshooting**:
- Check all required environment variables are set
- Verify service configuration files
- Review application startup logs
- Ensure all dependencies are properly installed

### 9999 - Unknown Internal Error
- **HTTP Status**: 500 Internal Server Error
- **Cause**: Unexpected server errors
- **User Message**: "An internal server error occurred"
- **Common Scenarios**:
  - Unhandled exceptions
  - System resource exhaustion
  - Unexpected service failures
  - Programming errors

**Example Response**:
```json
{
  "code": 9999,
  "success": false,
  "data": null,
  "message": "An internal server error occurred",
  "processing_time": 15.32
}
```

**Troubleshooting**:
- Check application logs for detailed error information
- Review system resource usage (CPU, memory, disk)
- Report the issue with request ID for investigation

## Error Handling Best Practices

### For Client Applications

1. **Always check the `success` field** before processing `data`
2. **Use business error codes** for specific error handling logic
3. **Display user-friendly messages** from the `message` field
4. **Implement retry logic** for 5xx errors with exponential backoff
5. **Log processing_time** for performance monitoring

### Example Error Handling Code

```javascript
async function processVideo(url) {
  try {
    const response = await fetch('/api/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    
    const result = await response.json();
    
    if (result.success) {
      return result.data;
    } else {
      // Handle specific error codes
      switch (result.code) {
        case 4001:
          throw new Error('Invalid video URL. Please check the URL and try again.');
        case 5001:
          throw new Error('Transcription service is temporarily unavailable. Please try again later.');
        case 5002:
          throw new Error('Analysis service is experiencing issues. Please try again later.');
        default:
          throw new Error(result.message || 'An unexpected error occurred.');
      }
    }
  } catch (error) {
    console.error('Video processing failed:', error);
    throw error;
  }
}
```

### For Service Monitoring

1. **Monitor error rate by code** to identify service issues
2. **Set up alerts** for high error rates on specific codes
3. **Track processing_time** to identify performance degradation
4. **Use request IDs** from logs for detailed error investigation

## Error Code Mapping Reference

| Exception Type | HTTP Status | Business Code | Retry Recommended |
|----------------|-------------|---------------|-------------------|
| URLParserError | 400 | 4001 | No |
| ValidationError | 400/422 | 4002 | No |
| ASRError | 503 | 5001 | Yes (with backoff) |
| LLMError | 502 | 5002 | Yes (with backoff) |
| FileHandlerError | 500 | 5003 | Depends on cause |
| OSSUploaderError | 503 | 5004 | Yes (with backoff) |
| ServiceInitializationError | 500 | 5005 | No |
| Unknown Exception | 500 | 9999 | No |

## Monitoring and Alerting

### Recommended Alerts

1. **High Error Rate**: > 5% of requests returning 5xx codes
2. **Service Unavailable**: > 10% of requests returning 5001 or 5004
3. **Processing Time**: Average processing time > 60 seconds
4. **Unknown Errors**: Any occurrence of code 9999

### Metrics to Track

- Error rate by business code
- Average processing time by endpoint
- Service availability (ASR, LLM, OSS)
- File upload success rate
- URL parsing success rate by platform

This error code reference should be used in conjunction with the main API documentation for comprehensive understanding of the ScriptParser API behavior.