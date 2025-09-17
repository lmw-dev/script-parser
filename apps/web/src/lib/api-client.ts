/**
 * API client for video parsing service
 * Following TypeScript best practices with strict typing
 */

import type { VideoParseRequest, VideoParseResponse } from "@/types/script-parser.types"

/**
 * Submits video for parsing via URL or file upload
 */
export const parseVideo = async (data: VideoParseRequest): Promise<VideoParseResponse> => {
  if (data.url) {
    // URL mode - send as JSON
    const response = await fetch("/api/parse", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: data.url }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json() as Promise<VideoParseResponse>
  }

  if (data.file) {
    // File mode - send as multipart/form-data
    const formData = new FormData()
    formData.append("file", data.file)

    const response = await fetch("/api/parse", {
      method: "POST",
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json() as Promise<VideoParseResponse>
  }

  throw new Error("Either URL or file must be provided")
}

/**
 * Mock implementation for development
 */
export const mockParseVideo = async (data: VideoParseRequest): Promise<VideoParseResponse> => {
  await new Promise((resolve) => setTimeout(resolve, 1000))

  const mockResponse: VideoParseResponse = {
    success: true,
    message: "Video parsed successfully",
    task_id: "mock-task-id",
    result: {
      transcript:
        "这是一个示例逐字稿内容。在这里会显示完整的视频转录文本，包含所有的对话、旁白和重要的音频信息。这个区域支持滚动查看完整内容，用户可以通过右上角的复制按钮一键复制全部文本。",
      analysis: {
        hook: "开头的吸引注意力的内容，通常是一个引人入胜的问题、惊人的事实或者情感化的陈述。",
        core: "视频的核心内容和主要价值点，包含关键信息、解决方案或者教学内容。",
        cta: "行动号召部分，引导观众进行下一步操作，如关注、点赞、评论或购买。",
      },
    },
  } as const

  return mockResponse
}
