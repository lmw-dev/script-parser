/**
 * Unit tests for API client module
 * Updated to test against the real API endpoint and data structure
 */

import { parseVideo } from '../api-client';
import type { VideoParseRequest, ApiAnalysisResult, VideoParseResponse } from '@/types/script-parser.types';

// Mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/parse`;

describe('api-client', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  afterEach(() => {
    mockFetch.mockReset();
  });

  describe('parseVideo', () => {
    describe('URL submission', () => {
      it('should make correct fetch call for URL request', async () => {
        const mockApiResponse: VideoParseResponse = {
          success: true,
          code: 0,
          data: { transcript: '', analysis: { llm_analysis: { hook: '', core: '', cta: '' } } },
        };
        mockFetch.mockResolvedValue({ ok: true, json: jest.fn().mockResolvedValue(mockApiResponse) });

        const request: VideoParseRequest = {
          type: 'url',
          url: 'https://www.douyin.com/video/123456789',
          file: null,
        };

        await parseVideo(request);

        expect(mockFetch).toHaveBeenCalledWith(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url: 'https://www.douyin.com/video/123456789' }),
        });
      });

      it('should return parsed result for successful URL request', async () => {
        const mockLlmAnalysis: ApiAnalysisResult = {
          hook: 'Amazing hook content',
          core: 'Deep core analysis',
          cta: 'Strong call to action',
        };
        const mockApiResponse: VideoParseResponse = {
            success: true,
            code: 0,
            data: { 
                transcript: 'test transcript', 
                analysis: { llm_analysis: mockLlmAnalysis }
            },
        };
        mockFetch.mockResolvedValue({ ok: true, json: jest.fn().mockResolvedValue(mockApiResponse) });

        const request: VideoParseRequest = {
          type: 'url',
          url: 'https://www.douyin.com/video/123456789',
          file: null,
        };

        const result = await parseVideo(request);

        expect(result).toEqual(mockLlmAnalysis);
      });
    });

    describe('File submission', () => {
      it('should make correct fetch call for file request', async () => {
        const mockFile = new File(['test content'], 'test.mp4', { type: 'video/mp4' });
        const mockApiResponse: VideoParseResponse = {
            success: true,
            code: 0,
            data: { transcript: '', analysis: { llm_analysis: { hook: '', core: '', cta: '' } } },
          };
        mockFetch.mockResolvedValue({ ok: true, json: jest.fn().mockResolvedValue(mockApiResponse) });

        const request: VideoParseRequest = {
          type: 'file',
          url: '',
          file: mockFile,
        };

        await parseVideo(request);

        expect(mockFetch).toHaveBeenCalledWith(apiUrl, {
          method: 'POST',
          body: expect.any(FormData),
        });

        const callArgs = mockFetch.mock.calls[0];
        const formData = callArgs[1].body as FormData;
        expect(formData.get('file')).toBe(mockFile);
        expect(formData.has('type')).toBe(false);
      });

      it('should throw an error if the API returns success: false', async () => {
        const mockApiResponse = { 
            success: false, 
            message: 'Processing failed in backend' 
        };
        mockFetch.mockResolvedValue({ ok: true, json: jest.fn().mockResolvedValue(mockApiResponse) });

        const request: VideoParseRequest = {
            type: 'url',
            url: 'https://www.douyin.com/video/123456789',
            file: null,
          };

        await expect(parseVideo(request)).rejects.toThrow('Processing failed in backend');
      });
    });

    // Error and input validation tests remain largely the same
    describe('Error handling', () => {
        it('should throw error when API returns failure response', async () => {
          const mockResponse = {
            ok: false,
            status: 400,
            statusText: 'Bad Request',
            text: jest.fn().mockResolvedValue('Invalid request format'),
          };
          mockFetch.mockResolvedValue(mockResponse);
  
          const request: VideoParseRequest = {
            type: 'url',
            url: 'https://www.douyin.com/video/123456789',
            file: null,
          };
  
          await expect(parseVideo(request)).rejects.toThrow('API request failed: 400 Bad Request - Invalid request format');
        });
      });
  
      describe('Input validation', () => {
        it('should throw error for invalid request type', async () => {
          const request = { type: 'invalid' } as any;
          await expect(parseVideo(request)).rejects.toThrow('Invalid request type: invalid');
        });
      });
  });
});