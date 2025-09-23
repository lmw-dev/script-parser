import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ResultSection } from './ResultSection';
import copy from 'copy-to-clipboard';
import * as utils from '@/lib/utils'; // Import all exports from utils
import type { AnalysisResult } from '@/types/script-parser.types';

// 1. Define the mock function first
const mockToastFn = jest.fn();

// 2. Mock the hooks and modules
jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: mockToastFn,
  }),
}));
jest.mock('copy-to-clipboard');

// Mock the utils module
jest.mock('@/lib/utils', () => ({
  ...jest.requireActual('@/lib/utils'), // Keep other utils functions working
  downloadAsMarkdown: jest.fn(),
}));

const mockCopy = copy as jest.Mock;
const mockDownload = utils.downloadAsMarkdown as jest.Mock;

// Mock data for the component
const mockResult: AnalysisResult = {
  transcript: 'This is the full transcript.',
  analysis: {
    hook: 'This is the hook.',
    core: 'This is the core.',
    cta: 'This is the CTA.',
  },
};

const defaultProps = {
  result: mockResult,
  onReset: jest.fn(),
  onDownload: jest.fn(), // This prop will be removed from the component, but is needed for the test to pass before refactoring
};

describe('ResultSection Component', () => {
  beforeEach(() => {
    // Clear mocks before each test
    mockCopy.mockClear();
    mockToastFn.mockClear();
    mockDownload.mockClear();
  });

  describe('Copy Functionality', () => {
    it('should call copy-to-clipboard and show success toast when copying transcript', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true); // Simulate successful copy
  
      render(<ResultSection {...defaultProps} />);
  
      const transcriptCard = screen.getByText('完整逐字稿').closest('[data-slot="card"]');
      const copyButton = transcriptCard!.querySelector('button');
  
      await user.click(copyButton!);
  
      // Assertions
      expect(mockCopy).toHaveBeenCalledTimes(1);
      expect(mockCopy).toHaveBeenCalledWith(mockResult.transcript);
      expect(mockToastFn).toHaveBeenCalledWith({
        title: '复制成功！',
        description: '完整逐字稿 已复制到您的剪贴板。',
      });
    });
  
    it('should call copy-to-clipboard with hook text when copying hook', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true);
  
      render(<ResultSection {...defaultProps} />);
  
      const hookCard = screen.getByText(/🚀 钩子/).closest('[data-slot="card"]');
      const copyButton = hookCard!.querySelector('button');
  
      await user.click(copyButton!);
  
      expect(mockCopy).toHaveBeenCalledTimes(1);
      expect(mockCopy).toHaveBeenCalledWith(mockResult.analysis.hook);
      expect(mockToastFn).toHaveBeenCalledWith({
        title: '复制成功！',
        description: '钩子 已复制到您的剪贴板。',
      });
    });
  
    it('should show a failure toast if copy-to-clipboard throws an error', async () => {
      const user = userEvent.setup();
      const errorMessage = 'Copy failed';
      mockCopy.mockImplementation(() => {
        throw new Error(errorMessage);
      });
  
      render(<ResultSection {...defaultProps} />);
  
      const transcriptCard = screen.getByText('完整逐字稿').closest('[data-slot="card"]');
      const copyButton = transcriptCard!.querySelector('button');
  
      await user.click(copyButton!);
  
      expect(mockCopy).toHaveBeenCalledTimes(1);
      expect(mockToastFn).toHaveBeenCalledWith({
        title: '复制失败',
        description: '无法访问剪贴板，请检查浏览器权限。',
        variant: 'destructive',
      });
    });
  });

  describe('Download Functionality', () => {
    it('should call downloadAsMarkdown when the download button is clicked', async () => {
      const user = userEvent.setup();
      render(<ResultSection {...defaultProps} />);

      const downloadButton = screen.getByRole('button', { name: /下载结果/i });
      await user.click(downloadButton);

      expect(mockDownload).toHaveBeenCalledTimes(1);
      expect(mockDownload).toHaveBeenCalledWith(mockResult);
    });
  });
});
