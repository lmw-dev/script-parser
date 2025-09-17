/**
 * Unit tests for validation utilities
 * Based on TOM-323 requirements
 */

import { describe, it, expect } from '@jest/globals'
import { isValidUrl, validateVideoFile, extractAndValidateUrl } from '../validation'

describe('validation utilities', () => {
  describe('isValidUrl', () => {
    it('should validate standard URLs', () => {
      expect(isValidUrl('https://www.douyin.com/video/123')).toBe(true)
      expect(isValidUrl('https://v.douyin.com/abc123')).toBe(true)
      expect(isValidUrl('https://www.xiaohongshu.com/explore/123')).toBe(true)
      expect(isValidUrl('http://xhslink.com/abc')).toBe(true)
    })

    it('should reject invalid URLs', () => {
      expect(isValidUrl('not-a-url')).toBe(false)
      expect(isValidUrl('')).toBe(false)
      expect(isValidUrl('https://unsupported-domain.com')).toBe(false)
    })
  })

  describe('extractAndValidateUrl', () => {
    it('should extract and validate URLs from Douyin share text', () => {
      const douyinShareText = `
        7.58 复制打开抖音，看看【用户名】的作品 https://v.douyin.com/ieFbPqc/
        更多精彩内容等你发现！
      `
      const result = extractAndValidateUrl(douyinShareText)
      expect(result.isValid).toBe(true)
      expect(result.extractedUrl).toBe('https://v.douyin.com/ieFbPqc')
    })

    it('should extract and validate URLs from Xiaohongshu share text', () => {
      const xiaohongshuShareText = `
        【标题】😍 http://xhslink.com/abc123，复制本条信息，打开【小红书】App查看精彩内容！
      `
      const result = extractAndValidateUrl(xiaohongshuShareText)
      expect(result.isValid).toBe(true)
      expect(result.extractedUrl).toBe('http://xhslink.com/abc123')
    })

    it('should handle text with multiple URLs and extract the first valid one', () => {
      const multiUrlText = `
        看看这个视频 https://v.douyin.com/valid123/ 还有这个 https://invalid-domain.com/test
      `
      const result = extractAndValidateUrl(multiUrlText)
      expect(result.isValid).toBe(true)
      expect(result.extractedUrl).toBe('https://v.douyin.com/valid123')
    })

    it('should return invalid for text without URLs', () => {
      const noUrlText = '这是一段没有链接的文本内容'
      const result = extractAndValidateUrl(noUrlText)
      expect(result.isValid).toBe(false)
      expect(result.extractedUrl).toBeUndefined()
      expect(result.error).toBe('No valid URL found in text')
    })

    it('should return invalid for text with only unsupported URLs', () => {
      const unsupportedUrlText = '查看这个链接 https://unsupported-domain.com/video/123'
      const result = extractAndValidateUrl(unsupportedUrlText)
      expect(result.isValid).toBe(false)
      expect(result.extractedUrl).toBeUndefined()
      expect(result.error).toBe('No supported video platform URL found')
    })

    it('should handle empty string', () => {
      const result = extractAndValidateUrl('')
      expect(result.isValid).toBe(false)
      expect(result.extractedUrl).toBeUndefined()
      expect(result.error).toBe('No valid URL found in text')
    })

    it('should handle complex Douyin share format', () => {
      const complexDouyinText = `
        复制这段描述，打开抖音搜索，观看视频。
        8.88 https://www.douyin.com/video/7123456789012345678 复制此链接，打开Dou音搜索，直接观看视频！
      `
      const result = extractAndValidateUrl(complexDouyinText)
      expect(result.isValid).toBe(true)
      expect(result.extractedUrl).toBe('https://www.douyin.com/video/7123456789012345678')
    })
  })

  describe('validateVideoFile', () => {
    it('should validate supported video file types', () => {
      const mp4File = new File([''], 'test.mp4', { type: 'video/mp4' })
      const result = validateVideoFile(mp4File)
      expect(result.isValid).toBe(true)
    })

    it('should validate MOV files with video/quicktime MIME type', () => {
      const movFile = new File([''], 'test.mov', { type: 'video/quicktime' })
      const result = validateVideoFile(movFile)
      expect(result.isValid).toBe(true)
    })

    it('should validate MOV files with video/mov MIME type', () => {
      const movFile = new File([''], 'test.mov', { type: 'video/mov' })
      const result = validateVideoFile(movFile)
      expect(result.isValid).toBe(true)
    })

    it('should reject unsupported file types', () => {
      const txtFile = new File([''], 'test.txt', { type: 'text/plain' })
      const result = validateVideoFile(txtFile)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('Unsupported file type')
    })

    it('should reject files that are too large', () => {
      const largeFile = new File(['x'.repeat(101 * 1024 * 1024)], 'large.mp4', { type: 'video/mp4' })
      const result = validateVideoFile(largeFile)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('File size exceeds 100MB limit')
    })
  })
})

