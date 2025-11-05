import { render, screen } from '@testing-library/react'
import { DonationSection } from './DonationSection'

describe('DonationSection', () => {
  it('should render two QR code images with correct src attributes', () => {
    const wechatQrPath = '/wechat_donate_qr.png'
    const alipayQrPath = '/alipay_donate_qr.png'

    render(
      <DonationSection
        wechatQrPath={wechatQrPath}
        alipayQrPath={alipayQrPath}
      />
    )

    const images = screen.getAllByRole('img')
    expect(images).toHaveLength(2)

    const wechatImg = screen.getByAltText(/微信/i)
    // Next.js Image component transforms src, so we check if it contains the path
    expect(wechatImg.getAttribute('src')).toContain(encodeURIComponent(wechatQrPath))

    const alipayImg = screen.getByAltText(/支付宝/i)
    expect(alipayImg.getAttribute('src')).toContain(encodeURIComponent(alipayQrPath))
  })

  it('should render the title and description text', () => {
    render(
      <DonationSection
        wechatQrPath="/wechat_donate_qr.png"
        alipayQrPath="/alipay_donate_qr.png"
      />
    )

    expect(screen.getByText(/支持开发者/i)).toBeInTheDocument()
    expect(
      screen.getByText(/完全自愿.*无任何强制/i)
    ).toBeInTheDocument()
  })

  it('should have data-testid attributes for tracking', () => {
    render(
      <DonationSection
        wechatQrPath="/wechat_donate_qr.png"
        alipayQrPath="/alipay_donate_qr.png"
      />
    )

    expect(screen.getByTestId('donation-section')).toBeInTheDocument()
    expect(screen.getByTestId('donation-wechat-qr')).toBeInTheDocument()
    expect(screen.getByTestId('donation-alipay-qr')).toBeInTheDocument()
  })

  it('should call onClick handler when QR code container is clicked', () => {
    const mockOnClick = jest.fn()

    render(
      <DonationSection
        wechatQrPath="/wechat_donate_qr.png"
        alipayQrPath="/alipay_donate_qr.png"
        onQrClick={mockOnClick}
      />
    )

    const wechatContainer = screen.getByTestId('donation-wechat-qr')
    wechatContainer.click()

    expect(mockOnClick).toHaveBeenCalledWith('wechat')
  })
})

