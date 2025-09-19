import json

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .services.asr_service import ASRError, ASRService
from .services.file_handler import FileHandler, FileHandlerError
from .services.llm_service import LLMError, create_llm_router_from_env
from .services.oss_uploader import OSSUploaderError, create_oss_uploader_from_env
from .services.url_parser import ShareURLParser, URLParserError

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
    success: bool
    data: AnalysisData | None = None
    message: str | None = None


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
    content_type = request.headers.get("content-type", "")

    # Handle JSON request with URL
    if "application/json" in content_type:
        try:
            body = await request.body()
            data = json.loads(body)
            if "url" in data:
                # Use ShareURLParser to parse the URL
                parser = ShareURLParser()
                try:
                    video_info = await parser.parse(data["url"])

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

                    return VideoParseResponse(
                        success=True,
                        data=AnalysisData(
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
                        ),
                    )
                except URLParserError as e:
                    raise HTTPException(status_code=400, detail=str(e)) from e
                except NotImplementedError as e:
                    raise HTTPException(status_code=501, detail=str(e)) from e
            else:
                raise HTTPException(
                    status_code=400, detail="Either URL or file must be provided."
                )
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=422, detail="Invalid JSON") from e

    # Handle multipart form data with file upload
    elif "multipart/form-data" in content_type:
        if file:
            file_handler = FileHandler()
            temp_file_info = None
            try:
                # Save uploaded file to temporary storage
                temp_file_info = await file_handler.save_upload_file(file)

                # Process file with ASR service using OSS integration
                transcript_text = f"Processed file: {temp_file_info.original_filename}"
                try:
                    # Create OSS uploader and ASR service with OSS integration
                    oss_uploader = create_oss_uploader_from_env()
                    asr_service = ASRService(oss_uploader=oss_uploader)
                    transcript_text = await asr_service.transcribe_from_file(
                        temp_file_info.file_path
                    )
                except (ASRError, ValueError, OSSUploaderError) as asr_error:
                    # If ASR or OSS fails, use fallback transcript with error info
                    transcript_text = f"File: {temp_file_info.original_filename} (Processing failed: {str(asr_error)})"
                except Exception as general_error:
                    # Catch any other unexpected errors
                    transcript_text = f"File: {temp_file_info.original_filename} (Processing failed: {str(general_error)})"

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

                return VideoParseResponse(
                    success=True,
                    data=AnalysisData(
                        transcript=transcript_text,
                        analysis={
                            "file_info": {
                                "file_path": str(temp_file_info.file_path),
                                "original_filename": temp_file_info.original_filename,
                                "size": temp_file_info.size,
                            },
                            "llm_analysis": llm_analysis
                        },
                    ),
                )
            except FileHandlerError as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
            finally:
                # Always cleanup temporary file
                if temp_file_info:
                    await FileHandler.cleanup(temp_file_info.file_path)
        elif url:
            # This handles form data with URL (should return 422 as per test)
            raise HTTPException(status_code=422, detail="URL should be sent as JSON")
        else:
            raise HTTPException(
                status_code=400, detail="Either URL or file must be provided."
            )

    # Handle form-encoded data (application/x-www-form-urlencoded)
    elif "application/x-www-form-urlencoded" in content_type:
        if url:
            # URL sent as form data instead of JSON - this is a validation error
            raise HTTPException(status_code=422, detail="URL should be sent as JSON")
        else:
            raise HTTPException(
                status_code=400, detail="Either URL or file must be provided."
            )

    # Handle empty request or other content types
    else:
        raise HTTPException(
            status_code=400, detail="Either URL or file must be provided."
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
