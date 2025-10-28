import { render, screen } from '@testing-library/react'
import { Footer } from './Footer'

describe('Footer', () => {
  const originalEnv = process.env

  beforeEach(() => {
    jest.resetModules()
    process.env = { ...originalEnv }
  })

  afterAll(() => {
    process.env = originalEnv
  })

  it('should render DonationSection when NEXT_PUBLIC_ENABLE_DONATION is true', () => {
    process.env.NEXT_PUBLIC_ENABLE_DONATION = 'true'

    render(<Footer />)

    expect(screen.getByTestId('donation-section')).toBeInTheDocument()
  })

  it('should not render DonationSection when NEXT_PUBLIC_ENABLE_DONATION is false', () => {
    process.env.NEXT_PUBLIC_ENABLE_DONATION = 'false'

    render(<Footer />)

    expect(screen.queryByTestId('donation-section')).not.toBeInTheDocument()
  })

  it('should not render DonationSection when NEXT_PUBLIC_ENABLE_DONATION is undefined', () => {
    delete process.env.NEXT_PUBLIC_ENABLE_DONATION

    render(<Footer />)

    expect(screen.queryByTestId('donation-section')).not.toBeInTheDocument()
  })

  it('should always render copyright section', () => {
    render(<Footer />)

    expect(screen.getByText(/All rights reserved/i)).toBeInTheDocument()
  })
})

