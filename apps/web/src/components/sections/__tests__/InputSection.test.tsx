/**
 * InputSection Component Tests
 * Testing TOM-489: Analysis Mode Selector UI
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { InputSection } from '../InputSection'
import type { InputSectionProps } from '@/types/script-parser.types'

// Mock dependencies
jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}))

describe('InputSection - Analysis Mode Selector (TOM-489)', () => {
  const defaultProps: InputSectionProps = {
    currentState: 'IDLE',
    inputValue: '',
    selectedFile: null,
    analysisMode: '',
    onInputChange: jest.fn(),
    onFileSelect: jest.fn(),
    onAnalysisModeChange: jest.fn(),
    onSubmit: jest.fn(),
    error: undefined,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  // ========================================
  // Test Suite 1: Select Component Rendering
  // ========================================
  describe('Select Component Rendering', () => {
    it('Test 1.1: should render Select component with placeholder', () => {
      render(<InputSection {...defaultProps} />)
      
      // Should show placeholder text when no mode is selected
      const selectTrigger = screen.getByRole('combobox')
      expect(selectTrigger).toBeInTheDocument()
      expect(screen.getByText(/请选择一个分析模式/i)).toBeInTheDocument()
    })

    it('Test 1.2: should display correct options when Select is opened', async () => {
      render(<InputSection {...defaultProps} />)
      
      // Open the select dropdown
      const selectTrigger = screen.getByRole('combobox')
      fireEvent.click(selectTrigger)
      
      // Should show both options
      await waitFor(() => {
        expect(screen.getByRole('option', { name: /通用叙事分析 \(V2\.0\)/i })).toBeInTheDocument()
        expect(screen.getByRole('option', { name: /科技产品评测 \(V3\.0\)/i })).toBeInTheDocument()
      })
    })
  })

  // ========================================
  // Test Suite 2: Button Disabled Logic
  // ========================================
  describe('Button Disabled Logic', () => {
    it('Test 2.1: should disable button when URL is valid but analysisMode is empty', () => {
      const props: InputSectionProps = {
        ...defaultProps,
        currentState: 'INPUT_VALID',
        inputValue: 'https://v.douyin.com/test',
        analysisMode: '', // Empty mode
      }
      
      render(<InputSection {...props} />)
      
      const submitButton = screen.getByRole('button', { name: /开始分析/i })
      expect(submitButton).toBeDisabled()
    })

    it('Test 2.2: should enable button when URL is valid AND analysisMode is selected', () => {
      const props: InputSectionProps = {
        ...defaultProps,
        currentState: 'INPUT_VALID',
        inputValue: 'https://v.douyin.com/test',
        analysisMode: 'tech', // Mode selected
      }
      
      render(<InputSection {...props} />)
      
      const submitButton = screen.getByRole('button', { name: /开始分析/i })
      expect(submitButton).not.toBeDisabled()
    })

    it('Test 2.3: should keep button disabled when URL is invalid even if mode is selected', () => {
      const props: InputSectionProps = {
        ...defaultProps,
        currentState: 'IDLE', // Invalid state
        inputValue: '',
        analysisMode: 'tech', // Mode selected but URL invalid
      }
      
      render(<InputSection {...props} />)
      
      const submitButton = screen.getByRole('button', { name: /开始分析/i })
      expect(submitButton).toBeDisabled()
    })
  })

  // ========================================
  // Test Suite 3: Select Interaction
  // ========================================
  describe('Select Interaction', () => {
    it('Test 3.1: should call onAnalysisModeChange callback when selecting a mode', async () => {
      const mockOnAnalysisModeChange = jest.fn()
      const props: InputSectionProps = {
        ...defaultProps,
        onAnalysisModeChange: mockOnAnalysisModeChange,
      }
      
      render(<InputSection {...props} />)
      
      // Open select and click an option
      const selectTrigger = screen.getByRole('combobox')
      fireEvent.click(selectTrigger)
      
      await waitFor(() => {
        const techOption = screen.getByRole('option', { name: /科技产品评测 \(V3\.0\)/i })
        fireEvent.click(techOption)
      })
      
      // Should call callback with correct value
      expect(mockOnAnalysisModeChange).toHaveBeenCalledWith('tech')
    })

    it('Test 3.2: should display the selected mode value', () => {
      const props: InputSectionProps = {
        ...defaultProps,
        analysisMode: 'general',
      }
      
      render(<InputSection {...props} />)
      
      // Should show the selected option text
      expect(screen.getByText(/通用叙事分析 \(V2\.0\)/i)).toBeInTheDocument()
    })
  })

  // ========================================
  // Test Suite 4: Integration Tests
  // ========================================
  describe('Integration: Full User Flow', () => {
    it('Test 4.1: should enable submit only after BOTH URL and mode are valid', async () => {
      const mockOnSubmit = jest.fn()
      const mockOnAnalysisModeChange = jest.fn()
      
      const { rerender } = render(
        <InputSection
          {...defaultProps}
          currentState="IDLE"
          inputValue=""
          analysisMode=""
          onAnalysisModeChange={mockOnAnalysisModeChange}
          onSubmit={mockOnSubmit}
        />
      )
      
      // Step 1: Button should be disabled initially
      let submitButton = screen.getByRole('button', { name: /开始分析/i })
      expect(submitButton).toBeDisabled()
      
      // Step 2: User enters valid URL (simulate parent state change)
      rerender(
        <InputSection
          {...defaultProps}
          currentState="INPUT_VALID"
          inputValue="https://v.douyin.com/test"
          analysisMode=""
          onAnalysisModeChange={mockOnAnalysisModeChange}
          onSubmit={mockOnSubmit}
        />
      )
      
      // Button still disabled (mode not selected)
      submitButton = screen.getByRole('button', { name: /开始分析/i })
      expect(submitButton).toBeDisabled()
      
      // Step 3: User selects mode (simulate mode selection)
      rerender(
        <InputSection
          {...defaultProps}
          currentState="INPUT_VALID"
          inputValue="https://v.douyin.com/test"
          analysisMode="tech"
          onAnalysisModeChange={mockOnAnalysisModeChange}
          onSubmit={mockOnSubmit}
        />
      )
      
      // Now button should be enabled
      submitButton = screen.getByRole('button', { name: /开始分析/i })
      expect(submitButton).not.toBeDisabled()
      
      // Step 4: User clicks submit
      fireEvent.click(submitButton)
      expect(mockOnSubmit).toHaveBeenCalled()
    })
  })
})


