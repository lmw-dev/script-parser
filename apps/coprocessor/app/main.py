from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="ScriptParser AI Coprocessor",
    description="AI service for audio transcription and intelligent analysis",
    version="1.0.0"
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

# 响应模型
class AudioProcessResponse(BaseModel):
    success: bool
    transcript: str
    message: str = ""

class TextAnalysisResponse(BaseModel):
    success: bool
    result: str
    message: str = ""

@app.get("/")
async def root():
    """Health check endpoint"""
    return JSONResponse(
        content={"message": "ScriptParser AI Coprocessor is running", "version": "1.0.0"},
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={"status": "healthy", "service": "ai-coprocessor"},
        headers={"Content-Type": "application/json; charset=utf-8"}
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
            message="Audio transcription successful"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio transcription failed: {str(e)}")

@app.post("/api/text/analyze", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """文本智能分析接口"""
    try:
        # TODO: 集成DeepSeek/Kimi LLM API
        # 这里是示例实现，需要替换为实际的LLM调用
        result = f"[示例] 文本分析结果 ({request.analysis_type}): {request.text[:100]}..."
        
        return TextAnalysisResponse(
            success=True,
            result=result,
            message="Text analysis successful"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)