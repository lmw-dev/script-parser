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

  it('should render Brevo form iframe', () => {
    render(<EmailSubscriptionForm />)
    
    const iframe = screen.getByTitle(/Email Subscription Form/i)
    expect(iframe).toBeInTheDocument()
    expect(iframe).toHaveAttribute('src')
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
})

