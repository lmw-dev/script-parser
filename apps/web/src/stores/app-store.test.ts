/**
 * Unit tests for the Zustand app store
 * Following a test-first approach for TOM-337
 */

import { useAppStore } from './app-store';
import { act } from '@testing-library/react';
import type { VideoParseRequest, AnalysisResult } from '@/types/script-parser.types';

// Mock data for testing
const mockRequest: VideoParseRequest = {
  type: 'url',
  url: 'https://www.douyin.com/video/123',
  file: null,
};

const mockResult: AnalysisResult = {
  transcript: 'This is a test transcript.',
  analysis: {
    hook: 'Test hook',
    core: 'Test core',
    cta: 'Test cta',
  },
};

const mockError = 'Something went wrong';

describe('useAppStore', () => {
  // Reset store before each test
  beforeEach(() => {
    act(() => {
      useAppStore.getState().reset();
    });
  });

  it('should have the correct initial state', () => {
    const { appState, requestData, resultData, error } = useAppStore.getState();
    expect(appState).toBe('IDLE');
    expect(requestData).toBeNull();
    expect(resultData).toBeNull();
    expect(error).toBeNull();
  });

  it('should handle the startProcessing action correctly', () => {
    act(() => {
      useAppStore.getState().startProcessing(mockRequest);
    });

    const { appState, requestData, error } = useAppStore.getState();
    expect(appState).toBe('PROCESSING');
    expect(requestData).toEqual(mockRequest);
    expect(error).toBeNull();
  });

  it('should handle the setSuccess action correctly', () => {
    act(() => {
      useAppStore.getState().setSuccess(mockResult);
    });

    const { appState, resultData } = useAppStore.getState();
    expect(appState).toBe('SUCCESS');
    expect(resultData).toEqual(mockResult);
  });

  it('should handle the setError action correctly', () => {
    act(() => {
      useAppStore.getState().setError(mockError);
    });

    const { appState, error, resultData } = useAppStore.getState();
    expect(appState).toBe('ERROR');
    expect(error).toBe(mockError);
    expect(resultData).toBeNull(); // Should clear previous results
  });

  it('should handle the reset action correctly', () => {
    // Set some state first
    act(() => {
      useAppStore.getState().startProcessing(mockRequest);
      useAppStore.getState().setSuccess(mockResult);
      useAppStore.getState().setError(mockError);
    });

    // Then reset
    act(() => {
      useAppStore.getState().reset();
    });

    const { appState, requestData, resultData, error } = useAppStore.getState();
    expect(appState).toBe('IDLE');
    expect(requestData).toBeNull();
    expect(resultData).toBeNull();
    expect(error).toBeNull();
  });
});