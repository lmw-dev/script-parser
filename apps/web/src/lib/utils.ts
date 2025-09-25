import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import copy from 'copy-to-clipboard'
import type { AnalysisResult } from '@/types/script-parser.types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Copies a string to the clipboard.
 * @param text The string to copy.
 * @returns true if successful, false otherwise.
 */
export const copyToClipboard = (text: string): boolean => {
  try {
    copy(text)
    return true
  } catch {
    return false
  }
}

/**
 * Generates a Markdown string from the analysis result and triggers a download.
 * @param result The analysis result object.
 * @param filename The desired filename for the download.
 * @param testMode If true, returns the content string instead of downloading.
 * @returns The Markdown content string if in test mode, otherwise void.
 */
export const downloadAsMarkdown = (
  result: AnalysisResult,
  filename: string = 'script-analysis.md',
  testMode: boolean = false
): string | void => {
  const content = `
# 视频脚本分析结果

## 完整逐字稿
${result.transcript}

## AI结构化分析
### 🚀 钩子 (Hook)
${result.analysis.hook}

### 💡 核心 (Core)
${result.analysis.core}

### 🎯 行动号召 (CTA)
${result.analysis.cta}
  `.trim()

  if (testMode) {
    return content
  }

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
