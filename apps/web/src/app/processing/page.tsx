import { ProcessingSection } from '@/components/sections/ProcessingSection';

// Mock data for the initial skeleton
const mockProcessingSteps = [
  "(1/3) 正在安全上传并解析视频...",
  "(2/3) 正在调用ASR服务，提取高质量逐字稿...",
  "(3/3) 正在调用LLM，进行AI结构化分析...",
];

export default function ProcessingPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <ProcessingSection step={1} steps={mockProcessingSteps} />
    </main>
  );
}