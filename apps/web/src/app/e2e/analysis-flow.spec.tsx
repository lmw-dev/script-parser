/**
 * End-to-end integration test for the entire analysis flow.
 * Based on TOM-340 requirements.
 * This test simulates the user journey from the home page to the result page,
 * verifying state transitions and navigation at each step.
 */

import { render, screen, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import HomePage from '@/app/page';
import ProcessingPage from '@/app/processing/page';
import ResultPage from '@/app/result/page';
import { useAppStore } from '@/stores/app-store';
import { parseVideo } from '@/lib/api-client';
import { useProgressAnimation } from '@/lib/progress-algorithm';
import { useEffect } from 'react';

// Mock dependencies
const mockRouterPush = jest.fn();
const mockRouterReplace = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockRouterPush,
    replace: mockRouterReplace,
  }),
}));

// Mock the api-client module
jest.mock('@/lib/api-client');
const mockedParseVideo = parseVideo as jest.Mock;

// Mock the progress animation hook
jest.mock('@/lib/progress-algorithm');
const mockUseProgressAnimation = useProgressAnimation as jest.Mock;

// Mock data for the E2E flow
const mockSuccessResult = {
  transcript: "This is the E2E test transcript.",
  analysis: { hook: "E2E Hook", core: "E2E Core", cta: "E2E CTA" },
};


describe('End-to-End Analysis Flow Integration Test', () => {

  beforeEach(() => {
    // Reset store and mocks before each test
    act(() => {
      useAppStore.getState().reset();
    });
    mockRouterPush.mockClear();
    mockRouterReplace.mockClear();
    mockedParseVideo.mockClear();
    mockUseProgressAnimation.mockClear();

    // Mock the progress animation to immediately call onComplete when the API is done
    mockUseProgressAnimation.mockImplementation((onComplete, apiCompleted) => {
        useEffect(() => {
          if (apiCompleted) {
            onComplete();
          }
        }, [apiCompleted, onComplete]);
  
        return { progress: 100, currentStage: 3, stageName: 'Done' };
      });
  });

  it('should navigate through the entire process on a successful submission', async () => {
    const user = userEvent.setup();

    // --- Phase 1: Home Page --- //
    const { unmount: unmountHomePage } = render(<HomePage />);

    // Simulate user input
    const urlInput = screen.getByPlaceholderText('在此处粘贴抖音/小红书分享链接...');
    await act(async () => {
        await user.type(urlInput, 'https://www.douyin.com/video/123');
    });

    // Simulate user click
    const submitButton = screen.getByRole('button', { name: /开始分析/i });
    await act(async () => {
        await user.click(submitButton);
    });

    // Assert Home Page behavior
    expect(useAppStore.getState().appState).toBe('PROCESSING');
    expect(useAppStore.getState().requestData?.url).toBe('https://www.douyin.com/video/123');
    expect(mockRouterPush).toHaveBeenCalledWith('/processing');

    // Unmount the home page to simulate navigation
    unmountHomePage();
    mockRouterPush.mockClear();

    // --- Phase 2: Processing Page --- //
    mockedParseVideo.mockResolvedValue(mockSuccessResult);

    const { unmount: unmountProcessingPage } = render(<ProcessingPage />);

    // Assert Processing Page behavior
    await waitFor(() => {
        expect(mockedParseVideo).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
        expect(useAppStore.getState().appState).toBe('SUCCESS');
        expect(useAppStore.getState().resultData).toEqual(mockSuccessResult);
    });

    await waitFor(() => {
        expect(mockRouterPush).toHaveBeenCalledWith('/result');
    });

    // Unmount the processing page
    unmountProcessingPage();
    mockRouterPush.mockClear();

    // --- Phase 3: Result Page --- //
    render(<ResultPage />);

    // Assert Result Page rendering
    await waitFor(() => {
        expect(screen.getByText("This is the E2E test transcript.")).toBeInTheDocument();
        expect(screen.getByText("E2E Hook")).toBeInTheDocument();
        expect(screen.getByText("E2E Core")).toBeInTheDocument();
        expect(screen.getByText("E2E CTA")).toBeInTheDocument();
    });
  });
});