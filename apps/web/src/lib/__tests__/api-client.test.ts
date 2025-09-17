/**
 * Unit tests for API client module
 * Test-First approach for TOM-325 implementation
 */

import { parseVideo } from '../api-client'
import type { VideoParseRequest, ApiAnalysisResult } from '@/types/script-parser.types'

// Mock global fetch
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('api-client', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    mockFetch.mockClear()
  })

  afterEach(() => {
    // Reset all mocks after each test
    mockFetch.mockReset()
  })

  describe('parseVideo', () => {
    describe('URL submission', () => {
      it('should make correct fetch call for URL request', async () => {
        // Arrange
        const mockResponse = {
          ok: true,
          json: jest.fn().mockResolvedValue({
            hook: 'Test hook',
            core: 'Test core content',
            cta: 'Test call to action'
          })
        }
        mockFetch.mockResolvedValue(mockResponse)

        const request: VideoParseRequest = {
          type: 'url',
          url: 'https://www.douyin.com/video/123456789',
          file: null
        }

        // Act
        await parseVideo(request)

        // Assert
        expect(mockFetch).toHaveBeenCalledWith('/api/parse', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            type: 'url',
            url: 'https://www.douyin.com/video/123456789'
          })
        })
      })

      it('should return parsed result for successful URL request', async () => {
        // Arrange
        const mockResult: ApiAnalysisResult = {
          hook: 'Amazing hook content',
          core: 'Deep core analysis',
          cta: 'Strong call to action'
        }
        const mockResponse = {
          ok: true,
          json: jest.fn().mockResolvedValue(mockResult)
        }
        mockFetch.mockResolvedValue(mockResponse)

        const request: VideoParseRequest = {
          type: 'url',
          url: 'https://www.douyin.com/video/123456789',
          file: null
        }

        // Act
        const result = await parseVideo(request)

        // Assert
        expect(result).toEqual(mockResult)
        expect(mockResponse.json).toHaveBeenCalled()
      })
    })

    describe('File submission', () => {
      it('should make correct fetch call for file request', async () => {
        // Arrange
        const mockFile = new File(['test content'], 'test.mp4', { type: 'video/mp4' })
        const mockResponse = {
          ok: true,
          json: jest.fn().mockResolvedValue({
            hook: 'File hook',
            core: 'File core content', 
            cta: 'File call to action'
          })
        }
        mockFetch.mockResolvedValue(mockResponse)

        const request: VideoParseRequest = {
          type: 'file',
          url: '',
          file: mockFile
        }

        // Act
        await parseVideo(request)

        // Assert
        expect(mockFetch).toHaveBeenCalledWith('/api/parse', {
          method: 'POST',
          body: expect.any(FormData)
        })

        // Verify FormData contains the file
        const callArgs = mockFetch.mock.calls[0]
        const formData = callArgs[1].body as FormData
        expect(formData.get('file')).toBe(mockFile)
        expect(formData.get('type')).toBe('file')
      })

      it('should return parsed result for successful file request', async () => {
        // Arrange
        const mockFile = new File(['test content'], 'test.mp4', { type: 'video/mp4' })
        const mockResult: ApiAnalysisResult = {
          hook: 'File analysis hook',
          core: 'File analysis core',
          cta: 'File analysis CTA'
        }
        const mockResponse = {
          ok: true,
          json: jest.fn().mockResolvedValue(mockResult)
        }
        mockFetch.mockResolvedValue(mockResponse)

        const request: VideoParseRequest = {
          type: 'file',
          url: '',
          file: mockFile
        }

        // Act
        const result = await parseVideo(request)

        // Assert
        expect(result).toEqual(mockResult)
        expect(mockResponse.json).toHaveBeenCalled()
      })
    })

    describe('Error handling', () => {
      it('should throw error when API returns failure response', async () => {
        // Arrange
        const mockResponse = {
          ok: false,
          status: 400,
          statusText: 'Bad Request',
          text: jest.fn().mockResolvedValue('Invalid request format')
        }
        mockFetch.mockResolvedValue(mockResponse)

        const request: VideoParseRequest = {
          type: 'url',
          url: 'https://www.douyin.com/video/123456789',
          file: null
        }

        // Act & Assert
        await expect(parseVideo(request)).rejects.toThrow('API request failed: 400 Bad Request - Invalid request format')
        expect(mockResponse.text).toHaveBeenCalled()
      })

      it('should throw error when fetch throws network error', async () => {
        // Arrange
        const networkError = new Error('Network connection failed')
        mockFetch.mockRejectedValue(networkError)

        const request: VideoParseRequest = {
          type: 'url',
          url: 'https://www.douyin.com/video/123456789',
          file: null
        }

        // Act & Assert
        await expect(parseVideo(request)).rejects.toThrow('Network connection failed')
      })

      it('should throw error when response JSON parsing fails', async () => {
        // Arrange
        const mockResponse = {
          ok: true,
          json: jest.fn().mockRejectedValue(new Error('Invalid JSON'))
        }
        mockFetch.mockResolvedValue(mockResponse)

        const request: VideoParseRequest = {
          type: 'url',
          url: 'https://www.douyin.com/video/123456789',
          file: null
        }

        // Act & Assert
        await expect(parseVideo(request)).rejects.toThrow('Invalid JSON')
      })
    })

    describe('Input validation', () => {
      it('should throw error for invalid request type', async () => {
        // Arrange
        const request = {
          type: 'invalid',
          url: '',
          file: null
        } as any

        // Act & Assert
        await expect(parseVideo(request)).rejects.toThrow('Invalid request type: invalid')
      })

      it('should throw error for URL request without URL', async () => {
        // Arrange
        const request: VideoParseRequest = {
          type: 'url',
          url: '',
          file: null
        }

        // Act & Assert
        await expect(parseVideo(request)).rejects.toThrow('URL is required for URL type requests')
      })

      it('should throw error for file request without file', async () => {
        // Arrange
        const request: VideoParseRequest = {
          type: 'file',
          url: '',
          file: null
        }

        // Act & Assert
        await expect(parseVideo(request)).rejects.toThrow('File is required for file type requests')
      })
    })
  })
})
