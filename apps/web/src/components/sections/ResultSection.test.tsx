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

// Mock data for the component (V3.0 structure)
const mockResult: AnalysisResult = {
  raw_transcript: 'This is the raw transcript with uh... um...',
  cleaned_transcript: 'This is the cleaned transcript.',
  analysis: {
    hook: 'This is the hook.',
    core: 'This is the core.',
    cta: 'This is the CTA.',
    key_quotes: ['Key Quote 1', 'Key Quote 2'],
  },
};

const defaultProps = {
  result: mockResult,
  onReset: jest.fn(),
};

describe('ResultSection Component', () => {
  beforeEach(() => {
    // Clear mocks before each test
    mockCopy.mockClear();
    mockToastFn.mockClear();
    mockDownload.mockClear();
  });

  describe('Copy Functionality', () => {
    it('should call copy-to-clipboard and show success toast when copying transcript (V3.0 - cleaned_transcript)', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true); // Simulate successful copy
  
      render(<ResultSection {...defaultProps} />);
  
      const transcriptCard = screen.getByText('完整逐字稿').closest('[data-slot="card"]');
      const copyButton = transcriptCard!.querySelector('button');
  
      await user.click(copyButton!);
  
      // Assertions - V3.0: should use cleaned_transcript
      expect(mockCopy).toHaveBeenCalledTimes(1);
      expect(mockCopy).toHaveBeenCalledWith(mockResult.cleaned_transcript);
      expect(mockToastFn).toHaveBeenCalledWith({
        title: '复制成功！',
        description: '完整逐字稿 已复制到您的剪贴板。',
      });
    });
  
    it('should call copy-to-clipboard with hook text when copying hook', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true);
  
      render(<ResultSection {...defaultProps} />);
  
      // Find the card containing the hook (now just shows "钩子")
      const hookCard = screen.getAllByText(/钩子/)[0].closest('[data-slot="card"]');
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

      const downloadButton = screen.getByRole('button', { name: /下载 Markdown/i });
      await user.click(downloadButton);

      expect(mockDownload).toHaveBeenCalledTimes(1);
      expect(mockDownload).toHaveBeenCalledWith(mockResult);
    });
  });

  describe('KeyQuotesCard (V3.0)', () => {
    it('should render KeyQuotesCard when key_quotes exist', () => {
      render(<ResultSection {...defaultProps} />);

      // Verify KeyQuotesCard title is rendered (now "金句" instead of full text)
      expect(screen.getByText('金句')).toBeInTheDocument();

      // Verify key quotes are rendered
      expect(screen.getByText(/Key Quote 1/)).toBeInTheDocument();
      expect(screen.getByText(/Key Quote 2/)).toBeInTheDocument();
    });

    it('should allow copying individual key quotes', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true);

      render(<ResultSection {...defaultProps} />);

      // Find all elements containing quote text
      const quotes = screen.getAllByText(/Key Quote/);
      // Find the parent cards and their buttons
      const firstQuoteCard = quotes[0].closest('[data-slot="card"]') || quotes[0].closest('.rounded-lg');
      const copyButtons = firstQuoteCard?.querySelectorAll('button') || [];

      // Should have at least one copy button (one per quote)
      expect(copyButtons.length).toBeGreaterThan(0);

      // Click the first copy button (first quote)
      await user.click(copyButtons[0]);

      expect(mockCopy).toHaveBeenCalledTimes(1);
      expect(mockCopy).toHaveBeenCalledWith(mockResult.analysis.key_quotes![0]);
      expect(mockToastFn).toHaveBeenCalledWith({
        title: '复制成功！',
        description: '金句 1 已复制到您的剪贴板。',
      });
    });

    it('should not render KeyQuotesCard when key_quotes is undefined', () => {
      const resultWithoutQuotes: AnalysisResult = {
        raw_transcript: 'Raw transcript',
        cleaned_transcript: 'Cleaned transcript',
        analysis: {
          hook: 'Hook',
          core: 'Core',
          cta: 'CTA',
        },
      };

      render(<ResultSection result={resultWithoutQuotes} onReset={jest.fn()} />);

      // KeyQuotesCard should not be rendered
      expect(screen.queryByText('金句提炼 (Key Quotes)')).not.toBeInTheDocument();
    });

    it('should not render KeyQuotesCard when key_quotes is empty array', () => {
      const resultWithEmptyQuotes: AnalysisResult = {
        raw_transcript: 'Raw transcript',
        cleaned_transcript: 'Cleaned transcript',
        analysis: {
          hook: 'Hook',
          core: 'Core',
          cta: 'CTA',
          key_quotes: [],
        },
      };

      render(<ResultSection result={resultWithEmptyQuotes} onReset={jest.fn()} />);

      // KeyQuotesCard should not be rendered
      expect(screen.queryByText('金句提炼 (Key Quotes)')).not.toBeInTheDocument();
    });
  });
});
