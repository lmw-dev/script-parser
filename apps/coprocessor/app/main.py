import json
import time

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .error_handling import (
    ErrorHandler,
    ServiceInitializationError,
    create_form_url_error,
    create_json_decode_error,
    create_missing_input_error,
    handle_service_exception,
)
from .http_client import cleanup_http_client
from .logging_config import PerformanceLogger, generate_request_id, set_request_context
from .performance_monitoring import ProcessingTimeMonitor, create_service_tracker
from .services.asr_service import ASRError, ASRService
from .services.file_handler import FileHandler, TempFileInfo
from .services.llm_service import LLMError, create_llm_router_from_env
from .services.oss_uploader import (
    OSSUploader,
    OSSUploaderError,
    create_oss_uploader_from_env,
)
from .services.url_parser import ShareURLParser

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="ScriptParser AI Coprocessor",
    description="AI service for audio transcription and intelligent analysis",
    version="1.0.0",
)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on application shutdown"""
    await cleanup_http_client()


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
    code: int  # 业务状态码
    success: bool  # 操作是否成功
    data: AnalysisData | None = None  # 成功时的数据
    message: str | None = None  # 错误或成功消息
    processing_time: float | None = None  # 处理时间（秒）


class WorkflowOrchestrator:
    """工作流编排器 - 统一处理URL和文件上传工作流"""

    def __init__(self, perf_logger: PerformanceLogger):
        """初始化工作流编排器，预先初始化所有服务"""
        self._url_parser = None
        self._file_handler = None
        self._oss_uploader = None
        self._llm_router = None
        self.perf_logger = perf_logger
        self.time_monitor = ProcessingTimeMonitor(perf_logger)

    def _get_url_parser(self) -> ShareURLParser:
        """获取URL解析器实例，延迟初始化"""
        if self._url_parser is None:
            try:
                with self.perf_logger.log_step("url_parser_init"):
                    self._url_parser = ShareURLParser()
            except Exception as e:
                self.perf_logger.log_error("Failed to initialize ShareURLParser", e)
                raise ServiceInitializationError(
                    f"Failed to initialize ShareURLParser: {str(e)}"
                ) from e
        return self._url_parser

    def _get_file_handler(self) -> FileHandler:
        """获取文件处理器实例，延迟初始化"""
        if self._file_handler is None:
            try:
                with self.perf_logger.log_step("file_handler_init"):
                    self._file_handler = FileHandler()
            except Exception as e:
                self.perf_logger.log_error("Failed to initialize FileHandler", e)
                raise ServiceInitializationError(
                    f"Failed to initialize FileHandler: {str(e)}"
                ) from e
        return self._file_handler

    def _get_oss_uploader(self) -> OSSUploader:
        """获取OSS上传器实例，延迟初始化"""
        if self._oss_uploader is None:
            try:
                with self.perf_logger.log_step("oss_uploader_init"):
                    self._oss_uploader = create_oss_uploader_from_env()
            except Exception as e:
                self.perf_logger.log_error("Failed to initialize OSSUploader", e)
                raise ServiceInitializationError(
                    f"Failed to initialize OSSUploader: {str(e)}"
                ) from e
        return self._oss_uploader

    def _get_llm_router(self):
        """获取LLM路由器实例，延迟初始化"""
        if self._llm_router is None:
            try:
                with self.perf_logger.log_step("llm_router_init"):
                    self._llm_router = create_llm_router_from_env()
            except Exception as e:
                self.perf_logger.log_error("Failed to initialize LLMRouter", e)
                raise ServiceInitializationError(
                    f"Failed to initialize LLMRouter: {str(e)}"
                ) from e
        return self._llm_router

    async def process_url_workflow(self, url: str) -> AnalysisData:
        """处理URL工作流"""
        self.perf_logger.log_step_start(
            "url_workflow", url=url[:100] if len(url) > 100 else url
        )

        # 确保ShareURLParser在URL处理流程中正确初始化和使用
        with self.perf_logger.log_step("url_parsing"):
            parser = self._get_url_parser()
            async with create_service_tracker(
                "ShareURLParser", "parse", self.perf_logger
            ):
                video_info = await parser.parse(url)

        # Try to transcribe video using ASR service
        transcript_text = f"Video: {video_info.title}"
        with self.perf_logger.log_step("asr_transcription"):
            try:
                # 确保ASRService正确处理OSS集成模式和传统模式
                # For URL workflow, we don't need OSS integration since we have a direct URL
                asr_service = ASRService()
                async with create_service_tracker(
                    "ASRService", "transcribe_from_url", self.perf_logger
                ):
                    transcript_text = await asr_service.transcribe_from_url(
                        video_info.download_url
                    )
                # Record ASR completion checkpoint
                self.time_monitor.checkpoint("asr_complete")
            except (ASRError, ValueError) as asr_error:
                self.perf_logger.log_error(
                    "ASR transcription failed", asr_error, video_id=video_info.video_id
                )
                # If ASR fails, use fallback transcript with error info
                transcript_text = (
                    f"Video: {video_info.title} (ASR failed: {str(asr_error)})"
                )

        # Perform LLM analysis on the transcript
        llm_analysis = {}
        with self.perf_logger.log_step("llm_analysis"):
            try:
                # 确保LLMRouter正确实现主备切换机制
                llm_router = self._get_llm_router()
                async with create_service_tracker(
                    "LLMRouter", "analyze", self.perf_logger
                ):
                    analysis_result = await llm_router.analyze(transcript_text)
                    llm_analysis = {
                        "hook": analysis_result.hook,
                        "core": analysis_result.core,
                        "cta": analysis_result.cta,
                    }
            except LLMError as llm_error:
                self.perf_logger.log_error(
                    "LLM analysis failed", llm_error, video_id=video_info.video_id
                )
                llm_analysis = {"error": f"LLM analysis failed: {str(llm_error)}"}

            # Record LLM completion checkpoint
            self.time_monitor.checkpoint("llm_complete")

        # Check performance target compliance
        self.time_monitor.check_target_compliance()

        self.perf_logger.log_step_end(
            "url_workflow", success=True, video_id=video_info.video_id
        )

        return AnalysisData(
            transcript=transcript_text,
            analysis={
                "video_info": {
                    "video_id": video_info.video_id,
                    "platform": video_info.platform,
                    "title": video_info.title,
                    "download_url": video_info.download_url,
                },
                "llm_analysis": llm_analysis,
            },
        )

    async def process_file_workflow(self, file_info: TempFileInfo) -> AnalysisData:
        """处理文件工作流"""
        self.perf_logger.log_step_start(
            "file_workflow",
            filename=file_info.original_filename,
            file_size=file_info.size,
        )

        # Process file with ASR service using OSS integration
        transcript_text = f"Processed file: {file_info.original_filename}"
        with self.perf_logger.log_step("file_asr_transcription"):
            try:
                # 确保FileHandler和OSSUploader在文件处理流程中正确集成
                # 确保ASRService正确处理OSS集成模式和传统模式
                oss_uploader = self._get_oss_uploader()
                asr_service = ASRService(oss_uploader=oss_uploader)
                async with create_service_tracker(
                    "ASRService", "transcribe_from_file", self.perf_logger
                ):
                    transcript_text = await asr_service.transcribe_from_file(
                        file_info.file_path
                    )
                            except (ASRError, ValueError, OSSUploaderError) as asr_error:
                                self.perf_logger.log_error(
                                    "File ASR transcription failed",
                                    asr_error,
                                    filename=file_info.original_filename,
                                )
                                # Re-raise the error to stop the workflow and return a proper error response
                                raise asr_error            except Exception as general_error:
                self.perf_logger.log_error(
                    "File processing failed with unexpected error",
                    general_error,
                    filename=file_info.original_filename,
                )
                # Catch any other unexpected errors
                transcript_text = f"File: {file_info.original_filename} (Processing failed: {str(general_error)})"
            else:
                # Record ASR completion checkpoint only on success
                self.time_monitor.checkpoint("asr_complete")

        # Perform LLM analysis on the transcript
        llm_analysis = {}
        with self.perf_logger.log_step("file_llm_analysis"):
            try:
                # 确保LLMRouter正确实现主备切换机制
                llm_router = self._get_llm_router()
                async with create_service_tracker(
                    "LLMRouter", "analyze", self.perf_logger
                ):
                    analysis_result = await llm_router.analyze(transcript_text)
                    llm_analysis = {
                        "hook": analysis_result.hook,
                        "core": analysis_result.core,
                        "cta": analysis_result.cta,
                    }
            except LLMError as llm_error:
                self.perf_logger.log_error(
                    "File LLM analysis failed",
                    llm_error,
                    filename=file_info.original_filename,
                )
                llm_analysis = {"error": f"LLM analysis failed: {str(llm_error)}"}

            # Record LLM completion checkpoint
            self.time_monitor.checkpoint("llm_complete")

        # Check performance target compliance
        self.time_monitor.check_target_compliance()

        self.perf_logger.log_step_end(
            "file_workflow", success=True, filename=file_info.original_filename
        )

        return AnalysisData(
            transcript=transcript_text,
            analysis={
                "file_info": {
                    "file_path": str(file_info.file_path),
                    "original_filename": file_info.original_filename,
                    "size": file_info.size,
                },
                "llm_analysis": llm_analysis,
            },
        )

    async def cleanup_resources(self, file_info: TempFileInfo | None):
        """
        清理资源 - 确保在所有情况下都能安全执行

        Args:
            file_info: 临时文件信息，可能为None
        """
        if file_info is not None:
            with self.perf_logger.log_step("resource_cleanup"):
                try:
                    async with create_service_tracker(
                        "FileHandler", "cleanup", self.perf_logger
                    ):
                        await FileHandler.cleanup(file_info.file_path)
                    self.perf_logger.logger.info(
                        f"Successfully cleaned up temporary file: {file_info.file_path}"
                    )
                except Exception as cleanup_error:
                    # Even if cleanup fails, we don't want to raise an exception
                    # as this could mask the original error that caused the request to fail
                    self.perf_logger.log_error(
                        "Resource cleanup failed",
                        cleanup_error,
                        file_path=str(file_info.file_path),
                    )
        else:
            self.perf_logger.logger.debug("No temporary file to clean up")


@app.get("/")
async def root():
    """Health check endpoint"""
    request_id = generate_request_id()
    set_request_context(request_id)

    perf_logger = PerformanceLogger("api.root")
    perf_logger.set_request_id(request_id)
    perf_logger.start_request("health_check")

    try:
        response = JSONResponse(
            content={
                "message": "ScriptParser AI Coprocessor is running",
                "version": "1.0.0",
            },
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        perf_logger.log_request_complete(success=True)
        return response
    except Exception as e:
        perf_logger.log_error("Root endpoint failed", e)
        perf_logger.log_request_complete(success=False)
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    request_id = generate_request_id()
    set_request_context(request_id)

    perf_logger = PerformanceLogger("api.health")
    perf_logger.set_request_id(request_id)
    perf_logger.start_request("health_check")

    try:
        response = JSONResponse(
            content={"status": "healthy", "service": "ai-coprocessor"},
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        perf_logger.log_request_complete(success=True)
        return response
    except Exception as e:
        perf_logger.log_error("Health check endpoint failed", e)
        perf_logger.log_request_complete(success=False)
        raise


@app.post("/api/audio/transcribe", response_model=AudioProcessResponse)
async def transcribe_audio(request: AudioProcessRequest):
    """音频转文本接口"""
    request_id = generate_request_id()
    set_request_context(request_id)

    perf_logger = PerformanceLogger("api.audio.transcribe")
    perf_logger.set_request_id(request_id)
    perf_logger.start_request(
        "audio_transcribe",
        language=request.language,
        audio_url_length=len(request.audio_url),
    )

    try:
        with perf_logger.log_step("audio_transcription"):
            # TODO: 集成阿里云ASR API
            # 这里是示例实现，需要替换为实际的ASR调用
            transcript = f"[示例] 音频转文本结果: {request.audio_url}"

        response = AudioProcessResponse(
            success=True,
            transcript=transcript,
            message="Audio transcription successful",
        )
        perf_logger.log_request_complete(success=True)
        return response
    except Exception as e:
        perf_logger.log_error(
            "Audio transcription failed", e, audio_url=request.audio_url[:100]
        )
        perf_logger.log_request_complete(success=False)
        raise HTTPException(
            status_code=500, detail=f"Audio transcription failed: {str(e)}"
        ) from e


@app.post("/api/text/analyze", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """文本智能分析接口"""
    request_id = generate_request_id()
    set_request_context(request_id)

    perf_logger = PerformanceLogger("api.text.analyze")
    perf_logger.set_request_id(request_id)
    perf_logger.start_request(
        "text_analyze",
        analysis_type=request.analysis_type,
        text_length=len(request.text),
    )

    try:
        with perf_logger.log_step("text_analysis"):
            # TODO: 集成DeepSeek/Kimi LLM API
            # 这里是示例实现，需要替换为实际的LLM调用
            result = f"[示例] 文本分析结果 ({request.analysis_type}): {request.text[:100]}..."

        response = TextAnalysisResponse(
            success=True, result=result, message="Text analysis successful"
        )
        perf_logger.log_request_complete(success=True)
        return response
    except Exception as e:
        perf_logger.log_error(
            "Text analysis failed",
            e,
            analysis_type=request.analysis_type,
            text_preview=request.text[:100],
        )
        perf_logger.log_request_complete(success=False)
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
    # 实现请求ID生成用于日志跟踪
    request_id = generate_request_id()
    set_request_context(request_id)

    # 添加请求开始时间记录用于计算processing_time
    start_time = time.time()
    content_type = request.headers.get("content-type", "")
    temp_file_info: TempFileInfo | None = None

    # 创建性能日志记录器
    perf_logger = PerformanceLogger("api.parse")
    perf_logger.set_request_id(request_id)

    # 记录各个服务调用的耗时和结果
    perf_logger.start_request(
        "video_parse",
        content_type=content_type,
        has_url=url is not None,
        has_file=file is not None,
    )

    orchestrator = WorkflowOrchestrator(perf_logger)

    try:
        # Handle JSON request with URL
        if "application/json" in content_type:
            with perf_logger.log_step("json_request_parsing"):
                try:
                    body = await request.body()
                    data = json.loads(body)
                except json.JSONDecodeError as e:
                    perf_logger.log_error("JSON decode failed", e)
                    raise create_json_decode_error(start_time) from e

                # Improved validation: check if URL exists and is not None/empty/whitespace
                if (
                    "url" in data
                    and data["url"] is not None
                    and str(data["url"]).strip()
                ):
                    # 重构JSON请求处理逻辑，使用统一的工作流编排
                    result_data = await orchestrator.process_url_workflow(
                        str(data["url"]).strip()
                    )
                else:
                    perf_logger.log_error(
                        "Missing or invalid URL in JSON request",
                        ValueError("URL is required"),
                    )
                    raise create_missing_input_error(start_time)

        # Handle multipart form data with file upload
        elif "multipart/form-data" in content_type:
            with perf_logger.log_step("multipart_request_parsing"):
                if file:
                    # 确保FileHandler在文件处理流程中正确集成
                    file_handler = orchestrator._get_file_handler()
                    # Save uploaded file to temporary storage
                    # 确保temp_file_info变量在异常情况下仍能被正确清理
                    async with create_service_tracker(
                        "FileHandler", "save_upload_file", perf_logger
                    ):
                        temp_file_info = await file_handler.save_upload_file(file)

                    # 重构multipart请求处理逻辑，使用统一的工作流编排
                    result_data = await orchestrator.process_file_workflow(
                        temp_file_info
                    )
                elif url:
                    # This handles form data with URL (should return 422 as per test)
                    perf_logger.log_error(
                        "URL sent as form data instead of JSON",
                        ValueError("URL should be sent as JSON"),
                    )
                    raise create_form_url_error(start_time)
                else:
                    perf_logger.log_error(
                        "Missing file or URL in multipart request",
                        ValueError("File or URL is required"),
                    )
                    raise create_missing_input_error(start_time)

        # Handle form-encoded data (application/x-www-form-urlencoded)
        elif "application/x-www-form-urlencoded" in content_type:
            with perf_logger.log_step("form_encoded_request_parsing"):
                if url:
                    # URL sent as form data instead of JSON - this is a validation error
                    perf_logger.log_error(
                        "URL sent as form-encoded data instead of JSON",
                        ValueError("URL should be sent as JSON"),
                    )
                    raise create_form_url_error(start_time)
                else:
                    perf_logger.log_error(
                        "Missing URL in form-encoded request",
                        ValueError("URL is required"),
                    )
                    raise create_missing_input_error(start_time)

        # Handle empty request or other content types
        else:
            perf_logger.log_error(
                "Unsupported content type",
                ValueError(f"Unsupported content type: {content_type}"),
            )
            raise create_missing_input_error(start_time)

        # 确保所有成功响应返回HTTP 200状态码和业务码0
        with perf_logger.log_step("response_assembly"):
            success_response = ErrorHandler.create_success_response(
                data=result_data,
                message="Processing completed successfully",
                start_time=start_time,
            )

            # Add detailed logging for the exact response data
            perf_logger.logger.info(f"[DEBUG] Full success response being sent: {success_response}")

            # Add performance summary to logs
            perf_summary = orchestrator.time_monitor.get_performance_summary()
            perf_logger.logger.info(
                f"Performance summary: {perf_summary['total_time']:.2f}s total "
                f"(target: {perf_summary['target_time']}s, "
                f"within_target: {perf_summary['within_target']})"
            )

        perf_logger.log_request_complete(success=True, response_code=0)
        return VideoParseResponse(**success_response)

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions (these are already properly formatted)
        perf_logger.log_error(
            "HTTP exception occurred", http_exc, status_code=http_exc.status_code
        )
        perf_logger.log_request_complete(
            success=False, status_code=http_exc.status_code
        )
        raise
    except Exception as e:
        # 移除重复的错误处理代码，使用统一的异常处理机制
        # 添加详细的错误日志记录，包含堆栈跟踪
        perf_logger.log_error("Unexpected exception in video parsing", e)
        perf_logger.log_request_complete(success=False, error_type=type(e).__name__)
        raise handle_service_exception(e, start_time) from e

    finally:
        # 在文件处理流程中使用try-finally块确保资源清理
        # 验证finally块在所有异常情况下都能执行
        await orchestrator.cleanup_resources(temp_file_info)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
