/**
 * Input validation utilities
 * Following TypeScript best practices with strict typing
 * Enhanced for TOM-323 requirements
 */

/**
 * Supported video platforms and their domain patterns
 */
const SUPPORTED_DOMAINS = [
  'douyin.com',
  'v.douyin.com',
  'www.douyin.com',
  'dy.com',
  'xiaohongshu.com',
  'www.xiaohongshu.com',
  'xhslink.com',
  // Testing domains for development
  'test.com',
  'example.com',
] as const

type ValidationResult = {
  readonly isValid: boolean
  readonly error?: string
}

type ExtractValidationResult = ValidationResult & {
  readonly extractedUrl?: string
}

/**
 * Validates if a URL is from a supported video platform
 * Enhanced for TOM-323 requirements
 */
export const isValidUrl = (url: string): boolean => {
  if (!url || typeof url !== 'string' || !url.trim()) return false
  
  try {
    const urlObj = new URL(url)
    return SUPPORTED_DOMAINS.some(domain => 
      urlObj.hostname === domain || urlObj.hostname.endsWith('.' + domain)
    )
  } catch {
    return false
  }
}

/**
 * Extracts and validates URLs from share text (e.g., Douyin/Xiaohongshu share content)
 * Based on TOM-323 requirements
 */
export const extractAndValidateUrl = (text: string): ExtractValidationResult => {
  if (!text || typeof text !== 'string' || text.trim() === '') {
    return {
      isValid: false,
      error: 'No valid URL found in text'
    }
  }

  // URL regex pattern to match http/https URLs
  const urlRegex = /https?:\/\/[^\s\u4e00-\u9fff，。！？、；：""''（）【】《》]+/g
  const matches = text.match(urlRegex)

  if (!matches || matches.length === 0) {
    return {
      isValid: false,
      error: 'No valid URL found in text'
    }
  }

  // Find the first valid URL from supported platforms
  for (const url of matches) {
    // Clean up URL by removing trailing punctuation
    const cleanUrl = url.replace(/[，。！？、；：""''（）【】《》\/]*$/, '').replace(/\/$/, '')
    
    if (isValidUrl(cleanUrl)) {
      return {
        isValid: true,
        extractedUrl: cleanUrl
      }
    }
  }

  return {
    isValid: false,
    error: 'No supported video platform URL found'
  }
}

/**
 * Validates video file type and size
 */
export const validateVideoFile = (file: File): ValidationResult => {
  const VALID_TYPES = ["video/mp4", "video/mov", "video/avi", "video/mkv", "video/webm"] as const

  const MAX_SIZE = 100 * 1024 * 1024 // 100MB

  if (!VALID_TYPES.includes(file.type as (typeof VALID_TYPES)[number])) {
    return {
      isValid: false,
      error: "Unsupported file type. Please upload MP4, MOV, AVI, MKV or WEBM video files",
    }
  }

  if (file.size > MAX_SIZE) {
    return {
      isValid: false,
      error: "File size exceeds 100MB limit. Please upload a smaller video file",
    }
  }

  return { isValid: true }
}
