/**
 * Unit tests for lib/utils.ts
 * Covers TOM-347: Markdown generation
 */

import { downloadAsMarkdown } from '../utils';
import type { AnalysisResult } from '@/types/script-parser.types';

describe('downloadAsMarkdown', () => {
  it('should generate the correct markdown string from the analysis result (V3.0)', () => {
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

    // V3.0: Expected content includes AI analysis, key_quotes, cleaned_transcript, and raw_transcript
    const expectedContent = `
# 视频脚本分析结果

## AI 结构化分析
### 🚀 钩子 (Hook)
${mockResult.analysis.hook}

### 💡 核心 (Core)
${mockResult.analysis.core}

### 🎯 行动号召 (CTA)
${mockResult.analysis.cta}

### ✨ 金句提炼 (Key Quotes)
1. ${mockResult.analysis.key_quotes![0]}
2. ${mockResult.analysis.key_quotes![1]}

---

---

## 完整逐字稿 (清洗后)
${mockResult.cleaned_transcript}

---

## 原始逐字稿
${mockResult.raw_transcript}
    `.trim();

    const generatedContent = (downloadAsMarkdown as any)(mockResult, 'test.md', true);

    expect(generatedContent).toBe(expectedContent);
  });

  it('should not include key_quotes section when key_quotes is empty or undefined', () => {
    const mockResultWithoutQuotes: AnalysisResult = {
      raw_transcript: 'This is the raw transcript.',
      cleaned_transcript: 'This is the cleaned transcript.',
      analysis: {
        hook: 'This is the hook.',
        core: 'This is the core.',
        cta: 'This is the CTA.',
      },
    };

    const generatedContent = (downloadAsMarkdown as any)(mockResultWithoutQuotes, 'test.md', true);

    // Should not contain key_quotes section
    expect(generatedContent).not.toContain('金句提炼');
    expect(generatedContent).not.toContain('Key Quotes');
    // Should still contain other sections
    expect(generatedContent).toContain('钩子 (Hook)');
    expect(generatedContent).toContain('完整逐字稿 (清洗后)');
    expect(generatedContent).toContain('原始逐字稿');
  });
});
