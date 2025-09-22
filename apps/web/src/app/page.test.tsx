/**
 * Integration test for the HomePage component
 * Tests the integration of component state, Zustand store, and routing
 * Based on TOM-338 requirements
 */

import { render, screen, fireEvent, act } from '@testing-library/react';
import HomePage from './page';
import { useAppStore } from '@/stores/app-store';
import { useRouter } from 'next/navigation';

// Mock the router specifically for this test suite
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

const mockPush = jest.fn();

describe('HomePage Integration', () => {
  beforeEach(() => {
    // Reset store and mocks before each test
    act(() => {
      useAppStore.getState().reset();
    });
    // Assign the mock implementation before each test
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    mockPush.mockClear();
  });

  it('handleSubmit should update Zustand store and navigate to /processing page', async () => {
    render(<HomePage />);

    const initialState = useAppStore.getState();
    expect(initialState.appState).toBe('IDLE');

    // Simulate user typing a valid URL
    const input = screen.getByPlaceholderText('在此处粘贴抖音/小红书分享链接...');
    await act(async () => {
      fireEvent.change(input, { target: { value: 'https://www.douyin.com/video/123' } });
    });

    // Get the submit button and click it
    const submitButton = screen.getByRole('button', { name: /开始分析/i });
    await act(async () => {
      fireEvent.click(submitButton);
    });

    // Assertions
    const finalState = useAppStore.getState();
    expect(finalState.appState).toBe('PROCESSING');
    expect(finalState.requestData).toEqual({
      type: 'url',
      url: 'https://www.douyin.com/video/123',
      file: null,
    });

    // Check if router.push was called correctly
    expect(mockPush).toHaveBeenCalledTimes(1);
    expect(mockPush).toHaveBeenCalledWith('/processing');
  });
});
