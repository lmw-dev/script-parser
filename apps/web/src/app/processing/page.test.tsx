/**
 * Integration test for the ProcessingPage
 * Based on TOM-339 requirements
 * Tests API calls, state updates, and navigation
 */

import { useEffect } from 'react';
import { render, act, waitFor } from '@testing-library/react';
import ProcessingPage from './page';
import { useAppStore } from '@/stores/app-store';
import { parseVideo } from '@/lib/api-client';
import { useRouter } from 'next/navigation';
import { useProgressAnimation } from '@/lib/progress-algorithm';
import type { VideoParseRequest, ApiAnalysisResult } from '@/types/script-parser.types';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));
jest.mock('@/lib/api-client', () => ({
  parseVideo: jest.fn(),
}));
jest.mock('@/lib/progress-algorithm');

const mockPush = jest.fn();
const mockReplace = jest.fn();
const mockParseVideo = parseVideo as jest.Mock;
const mockUseProgressAnimation = useProgressAnimation as jest.Mock;

const mockRequest: VideoParseRequest = {
  type: 'url',
  url: 'https://www.douyin.com/video/123',
  file: null,
};

const mockSuccessResult: ApiAnalysisResult = {
  hook: 'Test hook',
  core: 'Test core',
  cta: 'Test cta',
};

const mockError = new Error('API processing failed');

describe('ProcessingPage Integration', () => {
  beforeEach(() => {
    // Reset store and mocks before each test
    act(() => {
      useAppStore.getState().reset();
    });
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush, replace: mockReplace });
    mockPush.mockClear();
    mockReplace.mockClear();
    mockParseVideo.mockClear();
    mockUseProgressAnimation.mockClear();

    // Default mock implementation for the progress hook
    mockUseProgressAnimation.mockImplementation((onComplete, apiCompleted) => {
      useEffect(() => {
        if (apiCompleted) {
          onComplete();
        }
      }, [apiCompleted, onComplete]);

      return {
        progress: 50,
        currentStage: 2,
        stageName: 'mock stage',
      };
    });
  });

  describe('Successful API Flow', () => {
    it('should call API, update store to SUCCESS, and navigate to /result', async () => {
      // Arrange: Set initial state and mock successful API response
      act(() => {
        useAppStore.getState().startProcessing(mockRequest);
      });
      mockParseVideo.mockResolvedValue(mockSuccessResult);

      // Act
      render(<ProcessingPage />);

      // Assert
      await waitFor(() => {
        expect(mockParseVideo).toHaveBeenCalledTimes(1);
        expect(mockParseVideo).toHaveBeenCalledWith(mockRequest);
      });

      await waitFor(() => {
        const state = useAppStore.getState();
        expect(state.appState).toBe('SUCCESS');
        expect(state.resultData).toEqual(mockSuccessResult);
        expect(state.error).toBeNull();
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledTimes(1);
        expect(mockPush).toHaveBeenCalledWith('/result');
      });
    });
  });

  describe('Failed API Flow', () => {
    it('should call API, update store to ERROR, and navigate to /error', async () => {
      // Arrange: Set initial state and mock failed API response
      act(() => {
        useAppStore.getState().startProcessing(mockRequest);
      });
      mockParseVideo.mockRejectedValue(mockError);

      // Act
      render(<ProcessingPage />);

      // Assert
      await waitFor(() => {
        expect(mockParseVideo).toHaveBeenCalledTimes(1);
        expect(mockParseVideo).toHaveBeenCalledWith(mockRequest);
      });

      await waitFor(() => {
        const state = useAppStore.getState();
        expect(state.appState).toBe('ERROR');
        expect(state.error).toBe(mockError.message);
        expect(state.resultData).toBeNull();
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledTimes(1);
        expect(mockPush).toHaveBeenCalledWith('/error');
        expect(mockReplace).not.toHaveBeenCalled();
      });
    });
  });

  describe('Edge Case: No Request Data', () => {
    it('should redirect to the home page if no requestData is present', async () => {
      // Arrange: Store is in its initial state with requestData = null
      
      // Act
      render(<ProcessingPage />);

      // Assert
      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledTimes(1);
        expect(mockReplace).toHaveBeenCalledWith('/');
      });
      expect(mockParseVideo).not.toHaveBeenCalled();
      expect(mockPush).not.toHaveBeenCalled();
    });
  });
});