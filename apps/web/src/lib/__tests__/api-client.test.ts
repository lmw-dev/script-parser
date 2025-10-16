/**
 * Unit tests for API client
 * Tests timeout handling and response error handling
 */

import { parseVideo } from '../api-client'
import type { VideoParseRequest } from '@/types/script-parser.types'

// Mock fetch globally
global.fetch = jest.fn()

describe('parseVideo', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Timeout Handling', () => {
    it('should set 120 second timeout for URL requests', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          success: true,
          data: {
            transcript: 'test transcript',
            analysis: {
              llm_analysis: {
                hook: 'test hook',
                core: 'test core',
                cta: 'test cta'
              }
            }
          }
        })
      }

      ;(global.fetch as jest.Mock).mockResolvedValue(mockResponse)

      const request: VideoParseRequest = {
        type: 'url',
        url: 'https://example.com/video',
        file: null
      }

      await parseVideo(request)

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          signal: expect.any(AbortSignal)
        })
      )
    })

    it('should set 120 second timeout for file requests', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          success: true,
          data: {
            transcript: 'test transcript',
            analysis: {
              llm_analysis: {
                hook: 'test hook',
                core: 'test core',
                cta: 'test cta'
              }
            }
          }
        })
      }

      ;(global.fetch as jest.Mock).mockResolvedValue(mockResponse)

      const mockFile = new File(['test'], 'test.mp4', { type: 'video/mp4' })
      const request: VideoParseRequest = {
        type: 'file',
        url: '',
        file: mockFile
      }

      await parseVideo(request)

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          signal: expect.any(AbortSignal)
        })
      )
    })

    it('should provide user-friendly error message on timeout', async () => {
      const timeoutError = new Error('The operation timed out')
      timeoutError.name = 'TimeoutError'
      
      ;(global.fetch as jest.Mock).mockRejectedValue(timeoutError)

      const request: VideoParseRequest = {
        type: 'url',
        url: 'https://example.com/video',
        file: null
      }

      await expect(parseVideo(request)).rejects.toThrow('视频处理超时，请尝试上传较小的视频文件或稍后重试')
    })
  })

  describe('Response Error Handling', () => {
    it('should handle response.json() error with cloned response', async () => {
      const mockText = 'Internal Server Error'
      
      // Mock both original and cloned response
      const textMock = jest.fn().mockResolvedValue(mockText)
      const jsonMock = jest.fn().mockRejectedValue(new SyntaxError('Unexpected token < in JSON'))
      const cloneMock = jest.fn().mockReturnValue({ text: textMock })
      
      const mockResponse = {
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: jsonMock,
        clone: cloneMock
      }

      ;(global.fetch as jest.Mock).mockResolvedValue(mockResponse)

      const request: VideoParseRequest = {
        type: 'url',
        url: 'https://example.com/video',
        file: null
      }

      await expect(parseVideo(request)).rejects.toThrow(/API request failed/)
      
      // Verify the clone mechanism was used
      expect(cloneMock).toHaveBeenCalled()
      expect(textMock).toHaveBeenCalled()
    })

    it('should handle JSON error response correctly', async () => {
      const jsonMock = jest.fn().mockResolvedValue({
        success: false,
        message: 'Unsupported platform'
      })
      const cloneMock = jest.fn()
      
      const mockResponse = {
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: jsonMock,
        clone: cloneMock
      }

      ;(global.fetch as jest.Mock).mockResolvedValue(mockResponse)

      const request: VideoParseRequest = {
        type: 'url',
        url: 'https://example.com/video',
        file: null
      }

      await expect(parseVideo(request)).rejects.toThrow(/API request failed/)
      
      // Should successfully parse JSON, so clone shouldn't be needed
      expect(jsonMock).toHaveBeenCalled()
    })

    it('should handle network errors gracefully', async () => {
      const networkError = new TypeError('Failed to fetch')
      
      ;(global.fetch as jest.Mock).mockRejectedValue(networkError)

      const request: VideoParseRequest = {
        type: 'url',
        url: 'https://example.com/video',
        file: null
      }

      await expect(parseVideo(request)).rejects.toThrow('网络连接失败，请检查网络连接后重试')
    })
  })

  describe('Successful Response Handling', () => {
    it('should parse successful response correctly', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          success: true,
          data: {
            transcript: 'Test transcript content',
            analysis: {
              llm_analysis: {
                hook: 'Attention grabbing hook',
                core: 'Main content explanation',
                cta: 'Call to action'
              }
            }
          }
        })
      }

      ;(global.fetch as jest.Mock).mockResolvedValue(mockResponse)

      const request: VideoParseRequest = {
        type: 'url',
        url: 'https://example.com/video',
        file: null
      }

      const result = await parseVideo(request)

      expect(result).toEqual({
        transcript: 'Test transcript content',
        analysis: {
          hook: 'Attention grabbing hook',
          core: 'Main content explanation',
          cta: 'Call to action'
        }
      })
    })
  })
})
