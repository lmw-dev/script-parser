# ScriptParser AI Coprocessor API Documentation

## Overview

The ScriptParser AI Coprocessor provides intelligent video analysis services, including video URL parsing, audio transcription (ASR), and LLM-powered content analysis. This API supports both URL-based video processing and direct file uploads.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication for public endpoints. Service-specific API keys are configured via environment variables.

## Endpoints

### Health Check Endpoints

#### GET /

**Description:** Root health check endpoint

**Response:**
```json
{
  "message": "ScriptParser AI Coprocessor is running",
  "version": "1.0.0"
}
```

#### GET /health

**Description:** Detailed health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "ai-coprocessor"
}
```

### Video Processing Endpoint

#### POST /api/parse

**Description:** Main video processing endpoint that supports both URL parsing and file upload workflows.

**Content Types:**
- `application/json` - For URL-based processing
- `multipart/form-data` - For file upload processing

**Request Formats:**

##### URL Processing (JSON)
```json
{
  "url": "https://v.douyin.com/example-video-url"
}
```

##### File Upload (Multipart Form)
```
Content-Type: multipart/form-data

file: [video file binary data]
```

**Response Format:**

All responses follow a standardized format:

```json
{
  "code": 0,
  "success": true,
  "data": {
    "transcript": "Complete transcription text...",
    "analysis": {
      "video_info": {
        "video_id": "video123",
        "platform": "douyin",
        "title": "Video Title",
        "download_url": "https://..."
      },
      "llm_analysis": {
        "hook": "Engaging opening",
        "core": "Main content",
        "cta": "Call to action"
      }
    }
  },
  "message": "Processing completed successfully",
  "processing_time": 45.67
}
```

**Success Response (200 OK):**
- `code`: 0 (success)
- `success`: true
- `data`: Analysis results object
- `message`: Success message
- `processing_time`: Processing duration in seconds

**Error Response Format:**
```json
{
  "code": 4001,
  "success": false,
  "data": null,
  "message": "Failed to parse video URL",
  "processing_time": 12.34
}
```

## Error Codes

### Success Code
| Code | Description |
|------|-------------|
| 0    | Success     |

### Client Error Codes (4xxx)
| HTTP Status | Business Code | Description | Cause |
|-------------|---------------|-------------|-------|
| 400 | 4001 | URL parsing failed | Invalid or unsupported video URL |
| 400 | 4002 | Validation error | Missing required fields or invalid request format |
| 422 | 4002 | JSON format error | Invalid JSON in request body |
| 422 | 4002 | Form data error | URL sent as form data instead of JSON |

### Server Error Codes (5xxx)
| HTTP Status | Business Code | Description | Cause |
|-------------|---------------|-------------|-------|
| 503 | 5001 | ASR service unavailable | Audio transcription service is down or overloaded |
| 502 | 5002 | LLM service error | Language model service error or timeout |
| 500 | 5003 | File processing error | File handling or storage error |
| 503 | 5004 | OSS service unavailable | Object storage service is unavailable |
| 500 | 5005 | Service initialization error | Internal service configuration error |
| 500 | 9999 | Unknown internal error | Unexpected server error |

## Request Examples

### Process Video URL

```bash
curl -X POST "http://localhost:8000/api/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://v.douyin.com/ieFKPsNj/"
  }'
```

### Upload Video File

```bash
curl -X POST "http://localhost:8000/api/parse" \
  -F "file=@video.mp4"
```

## Response Examples

### Successful URL Processing

```json
{
  "code": 0,
  "success": true,
  "data": {
    "transcript": "这是一个关于人工智能的视频，讲述了AI技术的发展历程...",
    "analysis": {
      "video_info": {
        "video_id": "7234567890123456789",
        "platform": "douyin",
        "title": "AI技术发展趋势",
        "download_url": "https://aweme.snssdk.com/aweme/v1/play/?video_id=..."
      },
      "llm_analysis": {
        "hook": "开头通过提问吸引观众注意力",
        "core": "详细介绍了AI在各个领域的应用",
        "cta": "呼吁观众关注AI技术发展"
      }
    }
  },
  "message": "Processing completed successfully",
  "processing_time": 42.15
}
```

### Error Response - Invalid URL

```json
{
  "code": 4001,
  "success": false,
  "data": null,
  "message": "Failed to parse video URL",
  "processing_time": 2.34
}
```

### Error Response - ASR Service Unavailable

```json
{
  "code": 5001,
  "success": false,
  "data": null,
  "message": "ASR service is temporarily unavailable",
  "processing_time": 15.67
}
```

## Rate Limits

Currently, no rate limits are enforced. However, processing time targets are:
- Total processing time: ≤ 50 seconds for 1-minute videos
- URL parsing: ≤ 2 seconds
- File upload: ≤ 5 seconds
- ASR transcription: ≤ 30 seconds
- LLM analysis: ≤ 15 seconds

## Supported Platforms

### Video URL Platforms
- Douyin (抖音)
- Xiaohongshu (小红书)

### File Upload Formats
- MP4, AVI, MOV, WMV (video formats)
- MP3, WAV, M4A (audio formats)
- Maximum file size: 100MB

## Environment Configuration

The service requires the following environment variables:

### Required
- `DASHSCOPE_API_KEY`: Alibaba Cloud DashScope API key for ASR
- `DEEPSEEK_API_KEY`: DeepSeek API key for LLM analysis
- `KIMI_API_KEY`: Kimi API key for LLM fallback

### Optional OSS Configuration
- `ALIBABA_CLOUD_ACCESS_KEY_ID`: Alibaba Cloud Access Key ID
- `ALIBABA_CLOUD_ACCESS_KEY_SECRET`: Alibaba Cloud Access Key Secret
- `OSS_ENDPOINT`: OSS service endpoint (default: https://oss-cn-beijing.aliyuncs.com)
- `OSS_BUCKET_NAME`: OSS bucket name (default: scriptparser-audio)

### Performance Tuning
- `ASR_TIMEOUT`: ASR service timeout in seconds (default: 120)
- `LLM_TIMEOUT`: LLM service timeout in seconds (default: 30)
- `TOTAL_PROCESSING_TARGET`: Total processing time target in seconds (default: 50)
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 104857600 = 100MB)

## Error Handling

The API implements comprehensive error handling with:

1. **Graceful Degradation**: If ASR fails, a fallback transcript is provided
2. **Service Failover**: LLM service supports primary/backup switching
3. **Resource Cleanup**: Temporary files are automatically cleaned up
4. **Detailed Logging**: All errors are logged with request IDs for tracking

## Performance Monitoring

The API includes built-in performance monitoring:

- Request processing time tracking
- Service call duration monitoring
- Performance target compliance checking
- Detailed logging with request correlation IDs

## Security Considerations

1. **File Upload Security**: Uploaded files are sanitized and stored in temporary directories
2. **Input Validation**: All inputs are validated before processing
3. **Error Information**: Error messages are sanitized to prevent information leakage
4. **Resource Limits**: File size and processing time limits prevent resource exhaustion

## Development and Testing

### Running Tests

```bash
cd apps/coprocessor
python -m pytest -v
```

### Code Quality Checks

```bash
cd apps/coprocessor
ruff check .
ruff format .
```

### Local Development

```bash
cd apps/coprocessor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Support

For technical support or questions about the API, please refer to the project documentation or contact the development team.