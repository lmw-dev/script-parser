/**
 * Unit tests for lib/utils.ts
 * Covers TOM-347: Markdown generation
 */

import { downloadAsMarkdown } from '../utils';
import type { AnalysisResult } from '@/types/script-parser.types';

describe('downloadAsMarkdown', () => {
  it('should generate the correct markdown string from the analysis result', () => {
    const mockResult: AnalysisResult = {
      transcript: 'This is the transcript.',
      analysis: {
        hook: 'This is the hook.',
        core: 'This is the core.',
        cta: 'This is the CTA.',
      },
    };

    // This is a simplified way to test the generated content without mocking the DOM.
    // We will temporarily add a function to utils that just returns the content string.
    const expectedContent = `
# 视频脚本分析结果

## 完整逐字稿
${mockResult.transcript}

## AI结构化分析
### 🚀 钩子 (Hook)
${mockResult.analysis.hook}

### 💡 核心 (Core)
${mockResult.analysis.core}

### 🎯 行动号召 (CTA)
${mockResult.analysis.cta}
    `.trim();

    // We expect downloadAsMarkdown to not exist or not work yet, so this test will fail.
    // To make it testable, we'll have to modify the function signature slightly during implementation
    // to allow us to capture the generated content.
    
    // For now, we'll just have a placeholder test that will fail.
    const generatedContent = (downloadAsMarkdown as any)(mockResult, 'test.md', true);

    expect(generatedContent).toBe(expectedContent);
  });
});
