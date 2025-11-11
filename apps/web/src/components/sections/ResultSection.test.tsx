import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ResultSection } from './ResultSection';
import copy from 'copy-to-clipboard';
import * as utils from '@/lib/utils'; // Import all exports from utils
import type { V2NarrativeOutput, V3TechSpecOutput } from '@/types/script-parser.types';

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

// V2.0 Mock data (通用叙事分析)
const mockV2Result: V2NarrativeOutput = {
  raw_transcript: 'This is the raw transcript with uh... um...',
  cleaned_transcript: 'This is the cleaned transcript.',
  analysis: {
    hook: 'This is the hook.',
    core: 'This is the core.',
    cta: 'This is the CTA.',
    key_quotes: ['Key Quote 1', 'Key Quote 2'],
  },
};

// V3.0 Mock data (科技评测)
const mockV3Result: V3TechSpecOutput = {
  schema_type: 'v3_tech_spec',
  product_parameters: [
    { parameter: 'CPU', value: 'M4 Max' },
    { parameter: 'RAM', value: '64GB' },
    { parameter: '存储', value: '2TB SSD' },
  ],
  selling_points: [
    { 
      point: '性能提升30%', 
      context_snippet: 'M4 Max 芯片性能提升30%，多核跑分达到惊人的水平'
    },
    { 
      point: '续航时间更长', 
      context_snippet: '电池续航可达18小时，满足全天工作需求'
    },
  ],
  pricing_info: [
    { 
      product: 'MacBook Pro 16"', 
      price: '$3,499', 
      context_snippet: '16英寸 MacBook Pro 起售价为$3,499'
    },
  ],
  subjective_evaluation: {
    pros: ['性能强劲', '续航优秀', '屏幕出色'],
    cons: ['价格昂贵', '接口较少'],
  },
};

const defaultV2Props = {
  result: mockV2Result,
  onReset: jest.fn(),
};

const defaultV3Props = {
  result: mockV3Result,
  onReset: jest.fn(),
};

describe('ResultSection Component', () => {
  beforeEach(() => {
    // Clear mocks before each test
    mockCopy.mockClear();
    mockToastFn.mockClear();
    mockDownload.mockClear();
  });

  // ========================================
  // V2.0 向后兼容测试 (Existing Tests)
  // ========================================
  describe('Copy Functionality (V2.0 Backward Compatibility)', () => {
    it('should call copy-to-clipboard and show success toast when copying transcript (V3.0 - cleaned_transcript)', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true); // Simulate successful copy
  
      render(<ResultSection {...defaultV2Props} />);
  
      const transcriptCard = screen.getByText('完整逐字稿').closest('[data-slot="card"]');
      const copyButton = transcriptCard!.querySelector('button');
  
      await user.click(copyButton!);
  
      // Assertions - V3.0: should use cleaned_transcript
      expect(mockCopy).toHaveBeenCalledTimes(1);
      expect(mockCopy).toHaveBeenCalledWith(mockV2Result.cleaned_transcript);
      expect(mockToastFn).toHaveBeenCalledWith({
        title: '复制成功！',
        description: '完整逐字稿 已复制到您的剪贴板。',
      });
    });
  
    it('should call copy-to-clipboard with hook text when copying hook', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true);
  
      render(<ResultSection {...defaultV2Props} />);
  
      // Find the card containing the hook (now just shows "钩子")
      const hookCard = screen.getAllByText(/钩子/)[0].closest('[data-slot="card"]');
      const copyButton = hookCard!.querySelector('button');
  
      await user.click(copyButton!);
  
      expect(mockCopy).toHaveBeenCalledTimes(1);
      expect(mockCopy).toHaveBeenCalledWith(mockV2Result.analysis.hook);
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
  
      render(<ResultSection {...defaultV2Props} />);
  
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

  describe('Download Functionality (V2.0)', () => {
    it('should call downloadAsMarkdown when the download button is clicked', async () => {
      const user = userEvent.setup();
      render(<ResultSection {...defaultV2Props} />);

      const downloadButton = screen.getByRole('button', { name: /下载 Markdown/i });
      await user.click(downloadButton);

      expect(mockDownload).toHaveBeenCalledTimes(1);
      expect(mockDownload).toHaveBeenCalledWith(mockV2Result);
    });
  });

  describe('KeyQuotesCard (V2.0)', () => {
    it('should render KeyQuotesCard when key_quotes exist', () => {
      render(<ResultSection {...defaultV2Props} />);

      // Verify KeyQuotesCard title is rendered (now "金句" instead of full text)
      expect(screen.getByText('金句')).toBeInTheDocument();

      // Verify key quotes are rendered
      expect(screen.getByText(/Key Quote 1/)).toBeInTheDocument();
      expect(screen.getByText(/Key Quote 2/)).toBeInTheDocument();
    });

    it('should allow copying individual key quotes', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true);

      render(<ResultSection {...defaultV2Props} />);

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
      expect(mockCopy).toHaveBeenCalledWith(mockV2Result.analysis.key_quotes![0]);
      expect(mockToastFn).toHaveBeenCalledWith({
        title: '复制成功！',
        description: '金句 1 已复制到您的剪贴板。',
      });
    });

    it('should not render KeyQuotesCard when key_quotes is undefined', () => {
      const resultWithoutQuotes: V2NarrativeOutput = {
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
      const resultWithEmptyQuotes: V2NarrativeOutput = {
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

  // ========================================
  // V3.0 新功能测试 (TOM-494)
  // ========================================

  describe('Test Group 1: V2.0 Mode Rendering (Backward Compatibility)', () => {
    it('should render V2.0 narrative layout when schema_type is undefined', () => {
      render(<ResultSection {...defaultV2Props} />);

      // V2.0 卡片应该被渲染
      expect(screen.getByText('完整逐字稿')).toBeInTheDocument();
      expect(screen.getByText('钩子')).toBeInTheDocument();
      expect(screen.getByText('核心')).toBeInTheDocument();
      expect(screen.getByText('行动号召')).toBeInTheDocument();

      // V3.0 卡片不应该被渲染
      expect(screen.queryByText('产品参数')).not.toBeInTheDocument();
      expect(screen.queryByText('核心卖点')).not.toBeInTheDocument();
      expect(screen.queryByText('价格信息')).not.toBeInTheDocument();
      expect(screen.queryByText('评测总结')).not.toBeInTheDocument();
    });
  });

  describe('Test Group 2: V3.0 Mode Rendering', () => {
    it('should render V3.0 tech spec layout when schema_type is v3_tech_spec', () => {
      render(<ResultSection {...defaultV3Props} />);

      // V3.0 卡片应该被渲染
      expect(screen.getByText('产品参数')).toBeInTheDocument();
      expect(screen.getByText('核心卖点')).toBeInTheDocument();
      expect(screen.getByText('价格信息')).toBeInTheDocument();
      expect(screen.getByText('评测总结')).toBeInTheDocument();

      // V2.0 卡片不应该被渲染（除了操作按钮）
      expect(screen.queryByText('完整逐字稿')).not.toBeInTheDocument();
      expect(screen.queryByText('钩子')).not.toBeInTheDocument();
    });

    it('should render product parameters in a table format', () => {
      render(<ResultSection {...defaultV3Props} />);

      // 验证参数被渲染
      expect(screen.getByText('CPU')).toBeInTheDocument();
      expect(screen.getByText('M4 Max')).toBeInTheDocument();
      expect(screen.getByText('RAM')).toBeInTheDocument();
      expect(screen.getByText('64GB')).toBeInTheDocument();
    });

    it('should render selling points with context snippets', () => {
      render(<ResultSection {...defaultV3Props} />);

      // 验证卖点被渲染
      expect(screen.getByText(/性能提升30%/)).toBeInTheDocument();
      expect(screen.getByText(/续航时间更长/)).toBeInTheDocument();
      
      // 注意: context_snippet 默认是折叠的，需要展开才能看到
      // 验证折叠触发器存在（说明有原文引用）
      const sellingPointCard = screen.getByText('核心卖点').closest('[data-slot="card"]');
      expect(sellingPointCard).toBeInTheDocument();
    });

    it('should render pricing info correctly', () => {
      render(<ResultSection {...defaultV3Props} />);

      // 验证价格信息被渲染
      expect(screen.getByText(/MacBook Pro 16"/)).toBeInTheDocument();
      // 使用 getAllByText 因为价格可能出现在多处（价格标签和引用文本中）
      const priceElements = screen.getAllByText(/\$3,499/);
      expect(priceElements.length).toBeGreaterThan(0);
    });

    it('should render pros and cons in two columns', () => {
      render(<ResultSection {...defaultV3Props} />);

      // 验证优点被渲染
      expect(screen.getByText(/性能强劲/)).toBeInTheDocument();
      expect(screen.getByText(/续航优秀/)).toBeInTheDocument();
      expect(screen.getByText(/屏幕出色/)).toBeInTheDocument();

      // 验证缺点被渲染
      expect(screen.getByText(/价格昂贵/)).toBeInTheDocument();
      expect(screen.getByText(/接口较少/)).toBeInTheDocument();
    });
  });

  describe('Test Group 3: V3.0 Copy Functionality', () => {
    it('should copy product parameter when copy button clicked', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true);

      render(<ResultSection {...defaultV3Props} />);

      // 找到产品参数卡片中的第一个复制按钮
      const parameterCard = screen.getByText('产品参数').closest('[data-slot="card"]');
      const copyButtons = parameterCard?.querySelectorAll('button') || [];
      
      if (copyButtons.length > 1) {
        // 第一个可能是标题的按钮，找参数行的按钮
        await user.click(copyButtons[1]);
        
        expect(mockCopy).toHaveBeenCalledTimes(1);
        expect(mockToastFn).toHaveBeenCalledWith(
          expect.objectContaining({
            title: '复制成功！',
          })
        );
      }
    });

    it('should copy selling point when copy button clicked', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true);

      render(<ResultSection {...defaultV3Props} />);

      // 找到卖点卡片
      const sellingPointCard = screen.getByText('核心卖点').closest('[data-slot="card"]');
      const copyButtons = sellingPointCard?.querySelectorAll('button') || [];
      
      if (copyButtons.length > 0) {
        await user.click(copyButtons[1]);
        
        expect(mockCopy).toHaveBeenCalled();
        expect(mockToastFn).toHaveBeenCalled();
      }
    });

    it('should copy pricing info when copy button clicked', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true);

      render(<ResultSection {...defaultV3Props} />);

      // 找到价格卡片（注意：价格卡片在左列，第二个卡片位置）
      const pricingCard = screen.getByText('价格信息').closest('[data-slot="card"]');
      const copyButtons = pricingCard?.querySelectorAll('button[data-slot="button"]') || [];
      
      // 价格卡片中应该有复制按钮
      if (copyButtons.length > 0) {
        // 找到 Copy 图标的按钮（不是标题按钮）
        const copyButton = Array.from(copyButtons).find(btn => 
          btn.querySelector('.lucide-copy')
        );
        
        if (copyButton) {
          await user.click(copyButton);
          expect(mockCopy).toHaveBeenCalled();
        }
      }
    });

    it('should copy all V3.0 data as markdown when "全部复制" clicked', async () => {
      const user = userEvent.setup();
      mockCopy.mockReturnValue(true);

      render(<ResultSection {...defaultV3Props} />);

      // 找到"全部复制"按钮（在操作面板中）
      const copyAllButton = screen.queryByRole('button', { name: /全部复制/i });
      
      if (copyAllButton) {
        await user.click(copyAllButton);
        
        expect(mockCopy).toHaveBeenCalledTimes(1);
        // 验证复制的内容包含所有 V3.0 数据
        const copiedContent = mockCopy.mock.calls[0][0] as string;
        expect(copiedContent).toContain('产品参数');
        expect(copiedContent).toContain('CPU');
        expect(copiedContent).toContain('M4 Max');
      }
    });
  });

  describe('Test Group 4: Type Guards', () => {
    it('should correctly identify V2 narrative result', () => {
      const { container } = render(<ResultSection {...defaultV2Props} />);
      
      // V2.0 布局被渲染
      expect(container.querySelector('[data-testid="v2-narrative-layout"]') || screen.queryByText('完整逐字稿')).toBeTruthy();
    });

    it('should correctly identify V3 tech spec result', () => {
      const { container } = render(<ResultSection {...defaultV3Props} />);
      
      // V3.0 布局被渲染
      expect(container.querySelector('[data-testid="v3-tech-spec-layout"]') || screen.queryByText('产品参数')).toBeTruthy();
    });
  });
});
