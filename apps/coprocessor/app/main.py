import json
import time

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .error_handling import (
    ErrorHandler,
    create_form_url_error,
    create_json_decode_error,
    create_missing_input_error,
    handle_service_exception,
)
from .services.asr_service import ASRError, ASRService
from .services.file_handler import FileHandler, TempFileInfo
from .services.llm_service import LLMError, create_llm_router_from_env
from .services.oss_uploader import OSSUploaderError, create_oss_uploader_from_env
from .services.url_parser import ShareURLParser

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="ScriptParser AI Coprocessor",
    description="AI service for audio transcription and intelligent analysis",
    version="1.0.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求模型
class AudioProcessRequest(BaseModel):
    audio_url: str
    language: str = "zh-CN"


class TextAnalysisRequest(BaseModel):
    text: str
    analysis_type: str = "summary"


class VideoParseURLRequest(BaseModel):
    url: str


# 响应模型
class AudioProcessResponse(BaseModel):
    success: bool
    transcript: str
    message: str = ""


class TextAnalysisResponse(BaseModel):
    success: bool
    result: str
    message: str = ""


class AnalysisData(BaseModel):
    transcript: str
    analysis: dict


class VideoParseResponse(BaseModel):
    code: int                                    # 业务状态码
    success: bool                               # 操作是否成功
    data: AnalysisData | None = None           # 成功时的数据
    message: str | None = None                 # 错误或成功消息
    processing_time: float | None = None       # 处理时间（秒）


class WorkflowOrchestrator:
    """工作流编排器 - 统一处理URL和文件上传工作流"""

    async def process_url_workflow(self, url: str) -> AnalysisData:
        """处理URL工作流"""
        # Use ShareURLParser to parse the URL
        parser = ShareURLParser()
        video_info = await parser.parse(url)

        # Try to transcribe video using ASR service
        transcript_text = f"Video: {video_info.title}"
        try:
            asr_service = ASRService()
            transcript_text = await asr_service.transcribe_from_url(
                video_info.download_url
            )
        except (ASRError, ValueError) as asr_error:
            # If ASR fails, use fallback transcript with error info
            transcript_text = (
                f"Video: {video_info.title} (ASR failed: {str(asr_error)})"
            )

        # Perform LLM analysis on the transcript
        llm_analysis = {}
        try:
            llm_router = create_llm_router_from_env()
            analysis_result = await llm_router.analyze(transcript_text)
            llm_analysis = {
                "hook": analysis_result.hook,
                "core": analysis_result.core,
                "cta": analysis_result.cta
            }
        except LLMError as llm_error:
            llm_analysis = {"error": f"LLM analysis failed: {str(llm_error)}"}

        return AnalysisData(
            transcript=transcript_text,
            analysis={
                "video_info": {
                    "video_id": video_info.video_id,
                    "platform": video_info.platform,
                    "title": video_info.title,
                    "download_url": video_info.download_url,
                },
                "llm_analysis": llm_analysis
            },
        )

    async def process_file_workflow(self, file_info: TempFileInfo) -> AnalysisData:
        """处理文件工作流"""
        # Process file with ASR service using OSS integration
        transcript_text = f"Processed file: {file_info.original_filename}"
        try:
            # Create OSS uploader and ASR service with OSS integration
            oss_uploader = create_oss_uploader_from_env()
            asr_service = ASRService(oss_uploader=oss_uploader)
            transcript_text = await asr_service.transcribe_from_file(
                file_info.file_path
            )
        except (ASRError, ValueError, OSSUploaderError) as asr_error:
            # If ASR or OSS fails, use fallback transcript with error info
            transcript_text = f"File: {file_info.original_filename} (Processing failed: {str(asr_error)})"
        except Exception as general_error:
            # Catch any other unexpected errors
            transcript_text = f"File: {file_info.original_filename} (Processing failed: {str(general_error)})"

        # Perform LLM analysis on the transcript
        llm_analysis = {}
        try:
            llm_router = create_llm_router_from_env()
            analysis_result = await llm_router.analyze(transcript_text)
            llm_analysis = {
                "hook": analysis_result.hook,
                "core": analysis_result.core,
                "cta": analysis_result.cta
            }
        except LLMError as llm_error:
            llm_analysis = {"error": f"LLM analysis failed: {str(llm_error)}"}

        return AnalysisData(
            transcript=transcript_text,
            analysis={
                "file_info": {
                    "file_path": str(file_info.file_path),
                    "original_filename": file_info.original_filename,
                    "size": file_info.size,
                },
                "llm_analysis": llm_analysis
            },
        )

    async def cleanup_resources(self, file_info: TempFileInfo | None):
        """
        清理资源 - 确保在所有情况下都能安全执行
        
        Args:
            file_info: 临时文件信息，可能为None
        """
        if file_info is not None:
            try:
                await FileHandler.cleanup(file_info.file_path)
            except Exception:
                # Even if cleanup fails, we don't want to raise an exception
                # as this could mask the original error that caused the request to fail
                # In production, this should be logged
                pass


@app.get("/")
async def root():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "message": "ScriptParser AI Coprocessor is running",
            "version": "1.0.0",
        },
        headers={"Content-Type": "application/json; charset=utf-8"},
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={"status": "healthy", "service": "ai-coprocessor"},
        headers={"Content-Type": "application/json; charset=utf-8"},
    )


@app.post("/api/audio/transcribe", response_model=AudioProcessResponse)
async def transcribe_audio(request: AudioProcessRequest):
    """音频转文本接口"""
    try:
        # TODO: 集成阿里云ASR API
        # 这里是示例实现，需要替换为实际的ASR调用
        transcript = f"[示例] 音频转文本结果: {request.audio_url}"

        return AudioProcessResponse(
            success=True,
            transcript=transcript,
            message="Audio transcription successful",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Audio transcription failed: {str(e)}"
        ) from e


@app.post("/api/text/analyze", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """文本智能分析接口"""
    try:
        # TODO: 集成DeepSeek/Kimi LLM API
        # 这里是示例实现，需要替换为实际的LLM调用
        result = (
            f"[示例] 文本分析结果 ({request.analysis_type}): {request.text[:100]}..."
        )

        return TextAnalysisResponse(
            success=True, result=result, message="Text analysis successful"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Text analysis failed: {str(e)}"
        ) from e


@app.post("/api/parse", response_model=VideoParseResponse)
async def parse_video(
    request: Request,
    url: str | None = Form(None),
    file: UploadFile | None = File(None),
):
    """视频解析接口 - 支持URL和文件上传两种模式"""
    # 添加请求开始时间记录用于计算processing_time
    start_time = time.time()
    content_type = request.headers.get("content-type", "")
    temp_file_info: TempFileInfo | None = None
    orchestrator = WorkflowOrchestrator()

    try:
        # Handle JSON request with URL
        if "application/json" in content_type:
            try:
                body = await request.body()
                data = json.loads(body)
            except json.JSONDecodeError as e:
                raise create_json_decode_error(start_time) from e

            if "url" in data:
                # 重构JSON请求处理逻辑，使用统一的工作流编排
                result_data = await orchestrator.process_url_workflow(data["url"])
            else:
                raise create_missing_input_error(start_time)

        # Handle multipart form data with file upload
        elif "multipart/form-data" in content_type:
            if file:
                file_handler = FileHandler()
                # Save uploaded file to temporary storage
                # 确保temp_file_info变量在异常情况下仍能被正确清理
                temp_file_info = await file_handler.save_upload_file(file)

                # 重构multipart请求处理逻辑，使用统一的工作流编排
                result_data = await orchestrator.process_file_workflow(temp_file_info)
            elif url:
                # This handles form data with URL (should return 422 as per test)
                raise create_form_url_error(start_time)
            else:
                raise create_missing_input_error(start_time)

        # Handle form-encoded data (application/x-www-form-urlencoded)
        elif "application/x-www-form-urlencoded" in content_type:
            if url:
                # URL sent as form data instead of JSON - this is a validation error
                raise create_form_url_error(start_time)
            else:
                raise create_missing_input_error(start_time)

        # Handle empty request or other content types
        else:
            raise create_missing_input_error(start_time)

        # 确保所有成功响应返回HTTP 200状态码和业务码0
        success_response = ErrorHandler.create_success_response(
            data=result_data,
            message="Processing completed successfully",
            start_time=start_time
        )

        return VideoParseResponse(**success_response)

    except HTTPException:
        # Re-raise HTTP exceptions (these are already properly formatted)
        raise
    except Exception as e:
        # 移除重复的错误处理代码，使用统一的异常处理机制
        raise handle_service_exception(e, start_time) from e

    finally:
        # 在文件处理流程中使用try-finally块确保资源清理
        # 验证finally块在所有异常情况下都能执行
        await orchestrator.cleanup_resources(temp_file_info)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
