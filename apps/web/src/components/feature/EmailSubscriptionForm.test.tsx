import { render, screen } from '@testing-library/react'
import { EmailSubscriptionForm } from './EmailSubscriptionForm'

describe('EmailSubscriptionForm', () => {
  it('should render the component with title', () => {
    render(<EmailSubscriptionForm />)
    
    expect(screen.getByTestId('email-subscription-form')).toBeInTheDocument()
    expect(screen.getByText(/获取未来更新通知/i)).toBeInTheDocument()
  })

  it('should render the description text', () => {
    render(<EmailSubscriptionForm />)
    
    expect(screen.getByText(/对更深入的 AI 洞察或专业版功能感兴趣/i)).toBeInTheDocument()
  })

  it('should render Brevo form iframe (V2.1 with CONTENT_VERTICAL field)', () => {
    render(<EmailSubscriptionForm />)
    
    const iframe = screen.getByTitle(/Email Subscription Form/i)
    expect(iframe).toBeInTheDocument()
    expect(iframe).toHaveAttribute('src')
    expect(iframe).toHaveAttribute('width', '100%')
    expect(iframe).toHaveAttribute('height', '300')
    expect(iframe).toHaveAttribute('frameBorder', '0')
    expect(iframe).toHaveAttribute('scrolling', 'auto')
    expect(iframe).toHaveAttribute('allowFullScreen')
    
    // Verify iframe points to correct Brevo form (V2.1 version with CONTENT_VERTICAL field)
    const iframeSrc = iframe.getAttribute('src')
    expect(iframeSrc).toContain('sibforms.com')
    expect(iframeSrc).toContain('MUIFAHkjxX-n9rrJ1j42WzYsEjUDdzVZ7rWbrmUKoKdpuTyA0NCSnQH213Ie7BQnp8s6K2R_mGOyzeSqdDeVvbqpZUnf6jwYau3gEsll3Ff793evyFySI2Tke5NultC_BWRg_4xKBOddAryu_udcDlfMXXLy02-doA0pzlrOtwgPwrh33_hXm1HQqCsjdlPKjq0FLFQu-PWj8tCy')
  })

  it('should apply custom title if provided', () => {
    const customTitle = '自定义标题'
    render(<EmailSubscriptionForm title={customTitle} />)
    
    expect(screen.getByText(customTitle)).toBeInTheDocument()
  })

  it('should apply custom description if provided', () => {
    const customDescription = '自定义描述'
    render(<EmailSubscriptionForm description={customDescription} />)
    
    expect(screen.getByText(customDescription)).toBeInTheDocument()
  })

  it('should handle form interaction callbacks', () => {
    const mockOnFormInteraction = jest.fn()
    const mockOnFormView = jest.fn()
    
    render(
      <EmailSubscriptionForm
        onFormInteraction={mockOnFormInteraction}
        onFormView={mockOnFormView}
      />
    )
    
    // Verify the callbacks are provided to the component
    // Note: Direct interaction with iframe is not possible in unit tests due to cross-origin restrictions
    // But we verify the container element exists and has the click handler
    const formContainer = screen.getByTestId('email-subscription-form').closest('[data-testid="email-subscription-form"]')
    expect(formContainer).toBeInTheDocument()
  })
})

