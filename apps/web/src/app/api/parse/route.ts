/**
 * Temporary mock API route for /api/parse
 * This will be replaced with actual backend integration
 */

import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    // Get request data
    const contentType = request.headers.get('content-type') || ''
    
    let requestData: any
    
    if (contentType.includes('application/json')) {
      // URL request
      requestData = await request.json()
      console.log('[Mock API] Received URL request:', requestData)
    } else if (contentType.includes('multipart/form-data')) {
      // File request
      const formData = await request.formData()
      const file = formData.get('file') as File
      const type = formData.get('type') as string
      
      console.log('[Mock API] Received file request:', {
        type,
        fileName: file?.name,
        fileSize: file?.size,
        fileType: file?.type
      })
      
      requestData = { type, file: file?.name }
    } else {
      throw new Error('Unsupported content type')
    }

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Return mock analysis result
    const mockResult = {
      hook: "这是一个吸引人的开头，通过提出引人思考的问题或展示令人惊讶的事实来抓住观众的注意力。",
      core: "视频的核心内容包含了主要的价值点和关键信息。这里会详细解释产品特性、解决方案或者教学要点，为观众提供实质性的价值。",
      cta: "最后的行动号召部分，引导观众进行下一步操作，比如关注账号、点赞评论、购买产品或者分享给朋友。"
    }

    return NextResponse.json(mockResult, { status: 200 })

  } catch (error) {
    console.error('[Mock API] Error processing request:', error)
    
    return NextResponse.json(
      { 
        error: 'Processing failed', 
        message: error instanceof Error ? error.message : 'Unknown error',
        details: 'This is a mock API. The actual backend API is not yet implemented.'
      },
      { status: 500 }
    )
  }
}

// Handle unsupported methods
export async function GET() {
  return NextResponse.json(
    { error: 'Method not allowed', message: 'Only POST requests are supported' },
    { status: 405 }
  )
}
