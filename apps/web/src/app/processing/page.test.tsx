
import { render, screen } from '@testing-library/react';
import ProcessingPage from './page';

jest.mock('@/components/sections/ProcessingSection', () => ({
  ProcessingSection: ({ step, steps }: { step: number; steps: string[] }) => (
    <div>
      <h1>AI 正在分析中</h1>
      <p>Step {step} of {steps.length}</p>
      <p>{steps[step - 1]}</p>
    </div>
  ),
}));

describe('ProcessingPage', () => {
  it('should render the processing section correctly', () => {
    render(<ProcessingPage />);
    expect(screen.getByText('AI 正在分析中')).toBeInTheDocument();
  });
});
