
import { render, screen } from '@testing-library/react';
import ResultPage from './page';
import { AnalysisResult } from '@/types';

jest.mock('@/components/sections/ResultSection', () => ({
  ResultSection: ({ result }: { result: AnalysisResult }) => (
    <div>
      <h1>完整逐字稿</h1>
      <p>{result.transcript}</p>
    </div>
  ),
}));

describe('ResultPage', () => {
  it('should render the result section correctly', () => {
    render(<ResultPage />);
    expect(screen.getByText('完整逐字稿')).toBeInTheDocument();
  });
});
