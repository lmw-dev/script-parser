import { ResultSection } from '@/components/sections/ResultSection';
import { AnalysisResult } from '@/types';

// Mock data for the initial skeleton
const mockResult: AnalysisResult = {
  transcript: "这是模拟的完整逐字稿...",
  analysis: {
    hook: "这是模拟的钩子",
    core: "这是模拟的核心内容",
    cta: "这是模拟的行动号召",
  }
};

export default function ResultPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <ResultSection result={mockResult} onReset={() => {}} />
    </main>
  );
}