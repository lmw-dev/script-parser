/**
 * API client for video parsing service
 * Following TypeScript best practices with strict typing
 * Implementation for TOM-325 requirements
 */

import type { VideoParseRequest, AnalysisResult, VideoParseResponse } from "@/types/script-parser.types"

/**
 * Submits video for parsing via URL or file upload
 * Returns the analysis result directly
 */
export const parseVideo = async (request: VideoParseRequest): Promise<AnalysisResult> => {
  const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/parse`;

  // Input validation
  if (!request.type || (request.type !== 'url' && request.type !== 'file')) {
    throw new Error(`Invalid request type: ${request.type}`)
  }

  if (request.type === 'url') {
    if (!request.url || request.url.trim() === '') {
      throw new Error('URL is required for URL type requests')
    }
  }

  if (request.type === 'file') {
    if (!request.file) {
      throw new Error('File is required for file type requests')
    }
  }

  try {
    let response: Response

    if (request.type === 'url') {
      // URL mode - send as JSON
      response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: request.url
        }),
        // Extended timeout for video processing (2 minutes)
        signal: AbortSignal.timeout(120000),
      })
    } else {
      // File mode - send as multipart/form-data
      const formData = new FormData()
      formData.append("file", request.file!)

      response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
        // Extended timeout for video processing (2 minutes)
        signal: AbortSignal.timeout(120000),
      })
    }

    if (!response.ok) {
      // Clone the response to avoid "body stream already read" error
      const responseClone = response.clone();
      
      // Attempt to parse the JSON error response from the API
      try {
        const errorData: VideoParseResponse = await response.json();
        throw new Error(errorData.message || `API request failed with status ${response.status}`);
      } catch (jsonError) {
        // If the error response isn't JSON, fall back to the raw text from the cloned response
        try {
          const errorText = await responseClone.text();
          throw new Error(`API request failed: ${response.status} ${response.statusText}${errorText ? ` - ${errorText}` : ''}`);
        } catch {
          // If both fail, provide a generic error message
          throw new Error(`API request failed with status ${response.status} ${response.statusText}`);
        }
      }
    }

    const responseData: VideoParseResponse = await response.json();

    // Also handle cases where the HTTP request was successful, but the business logic failed
    if (!responseData.success || !responseData.data) {
      throw new Error(responseData.message || 'API returned a non-successful status.');
    }

    // Parse and transform the result to match frontend data structure
    const llmAnalysis = responseData.data.analysis?.llm_analysis;

    if (!llmAnalysis) {
        throw new Error('LLM analysis data is missing in the API response.');
    }

    // V3.0: Map BackendData to AnalysisResult (frontend structure)
    // Note: llmAnalysis is ApiAnalysisResult which includes key_quotes
    const frontendResult: AnalysisResult = {
        raw_transcript: responseData.data.raw_transcript,
        cleaned_transcript: responseData.data.cleaned_transcript,
        analysis: llmAnalysis, // llmAnalysis already contains key_quotes (V3.0)
    };
    return frontendResult;

  } catch (error) {
    // Handle timeout errors specifically
    if (error instanceof Error && error.name === 'TimeoutError') {
      throw new Error('视频处理超时，请尝试上传较小的视频文件或稍后重试');
    }
    
    // Handle network errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('网络连接失败，请检查网络连接后重试');
    }
    
    // Re-throw other errors to be handled by the caller
    throw error
  }
}

/**
 * Mock implementation for development
 */
export const mockParseVideo = async (): Promise<VideoParseResponse> => {
  await new Promise((resolve) => setTimeout(resolve, 1000))

  // V3.0 Mock Response Structure
  const mockResponse: VideoParseResponse = {
    success: true,
    code: 200,
    message: "Video parsed successfully",
    data: {
      raw_transcript:
        "这是一个示例原始逐字稿内容（未清洗）。嗯... 那个... 这个视频转录文本，包含所有的对话、旁白和重要的音频信息...",
      cleaned_transcript:
        "这是一个示例逐字稿内容。在这里会显示完整的视频转录文本，包含所有的对话、旁白和重要的音频信息。这个区域支持滚动查看完整内容，用户可以通过右上角的复制按钮一键复制全部文本。",
      analysis: {
        llm_analysis: {
          hook: "开头的吸引注意力的内容，通常是一个引人入胜的问题、惊人的事实或者情感化的陈述。",
          core: "视频的核心内容和主要价值点，包含关键信息、解决方案或者教学内容。",
          cta: "行动号召部分，引导观众进行下一步操作，如关注、点赞、评论或购买。",
          key_quotes: [
            "这是一个示例金句，具有高度概括性和传播价值。",
            "这是另一个示例金句，适合用于社交媒体分享。"
          ],
        },
      },
    },
  }

  return mockResponse
}
