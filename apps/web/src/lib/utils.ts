import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import copy from 'copy-to-clipboard'

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
  } catch (error) {
    console.error('Failed to copy text to clipboard:', error)
    return false
  }
}
