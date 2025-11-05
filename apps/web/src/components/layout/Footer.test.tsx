import { render, screen } from '@testing-library/react'
import { Footer } from './Footer'

describe('Footer', () => {
  it('should render footer navigation sections', () => {
    render(<Footer />)

    expect(screen.getByText('AI 脚本快拆')).toBeInTheDocument()
    expect(screen.getByText('导航')).toBeInTheDocument()
    expect(screen.getByText('关注我')).toBeInTheDocument()
  })

  it('should render footer links', () => {
    render(<Footer />)

    // Use getAllByText since "博客" appears in both navigation and social links
    const homeLinks = screen.getAllByText('首页')
    expect(homeLinks.length).toBeGreaterThan(0)
    
    const priceLinks = screen.getAllByText('价格')
    expect(priceLinks.length).toBeGreaterThan(0)
    
    const blogLinks = screen.getAllByText('博客')
    expect(blogLinks.length).toBeGreaterThan(0)
  })

  it('should render social media links', () => {
    render(<Footer />)

    expect(screen.getByText('GitHub')).toBeInTheDocument()
    expect(screen.getByText('Twitter')).toBeInTheDocument()
    expect(screen.getByText('小红书')).toBeInTheDocument()
  })

  it('should always render copyright section', () => {
    render(<Footer />)

    expect(screen.getByText(/All rights reserved/i)).toBeInTheDocument()
  })

  it('should not render DonationSection or EmailSubscriptionForm', () => {
    render(<Footer />)

    // These sections have been moved to the result page
    expect(screen.queryByTestId('donation-section')).not.toBeInTheDocument()
    expect(screen.queryByTestId('email-subscription-form')).not.toBeInTheDocument()
  })
})

