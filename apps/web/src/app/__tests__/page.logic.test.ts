/**
 * Unit tests for page.tsx file handling logic
 * Following TOM-324 requirements with test-first approach
 */

// Jest globals are available in test environment
import type { AppState } from '../../types/script-parser.types'

// Mock setState functions for testing
type MockSetState<T> = jest.MockedFunction<(value: T | ((prev: T) => T)) => void>

interface FileHandlingContext {
  setAppState: MockSetState<AppState>
  setSelectedFile: MockSetState<File | null>
  setInputValue: MockSetState<string>
  setError: MockSetState<string>
}

// Mock validation results
interface ValidationResult {
  isValid: boolean
  error?: string
}

// Import the actual implementation
import { handleFileChangeLogic } from '../page'

describe('page.tsx file handling logic', () => {
  let mockContext: FileHandlingContext
  let mockValidateVideoFile: jest.MockedFunction<(file: File) => ValidationResult>
  
  beforeEach(() => {
    mockContext = {
      setAppState: jest.fn(),
      setSelectedFile: jest.fn(),
      setInputValue: jest.fn(),
      setError: jest.fn(),
    }
    
    mockValidateVideoFile = jest.fn()
    jest.clearAllMocks()
  })

  describe('handleFileChange function', () => {
    it('should handle valid file selection correctly', () => {
      // Arrange
      const validFile = new File(['test content'], 'test-video.mp4', {
        type: 'video/mp4',
        lastModified: Date.now(),
      })
      
      // Mock validation to return success
      mockValidateVideoFile.mockReturnValue({
        isValid: true,
      })
      
      // Act
      handleFileChangeLogic(validFile, mockContext, mockValidateVideoFile)
      
      // Assert
      expect(mockValidateVideoFile).toHaveBeenCalledWith(validFile)
      expect(mockContext.setAppState).toHaveBeenCalledWith('INPUT_VALID')
      expect(mockContext.setSelectedFile).toHaveBeenCalledWith(validFile)
      expect(mockContext.setInputValue).toHaveBeenCalledWith('')
      expect(mockContext.setError).toHaveBeenCalledWith('')
    })

    it('should handle invalid file type correctly', () => {
      // Arrange
      const invalidFile = new File(['test content'], 'test-image.png', {
        type: 'image/png',
        lastModified: Date.now(),
      })
      
      const errorMessage = '不支持的文件类型'
      
      // Mock validation to return error
      mockValidateVideoFile.mockReturnValue({
        isValid: false,
        error: errorMessage,
      })
      
      // Act
      handleFileChangeLogic(invalidFile, mockContext, mockValidateVideoFile)
      
      // Assert
      expect(mockValidateVideoFile).toHaveBeenCalledWith(invalidFile)
      expect(mockContext.setAppState).toHaveBeenCalledWith('ERROR')
      expect(mockContext.setSelectedFile).toHaveBeenCalledWith(null)
      expect(mockContext.setError).toHaveBeenCalledWith(errorMessage)
    })

    it('should handle file size exceeding limit correctly', () => {
      // Arrange - Create a large file (150MB)
      const largeFile = new File(['large content'], 'large-video.mp4', {
        type: 'video/mp4',
        lastModified: Date.now(),
      })
      
      const errorMessage = '文件大小超过限制'
      
      // Mock validation to return size error
      mockValidateVideoFile.mockReturnValue({
        isValid: false,
        error: errorMessage,
      })
      
      // Act
      handleFileChangeLogic(largeFile, mockContext, mockValidateVideoFile)
      
      // Assert
      expect(mockValidateVideoFile).toHaveBeenCalledWith(largeFile)
      expect(mockContext.setAppState).toHaveBeenCalledWith('ERROR')
      expect(mockContext.setSelectedFile).toHaveBeenCalledWith(null)
      expect(mockContext.setError).toHaveBeenCalledWith(errorMessage)
    })

    it('should handle null file input correctly', () => {
      // Act
      handleFileChangeLogic(null, mockContext, mockValidateVideoFile)
      
      // Assert
      expect(mockValidateVideoFile).not.toHaveBeenCalled()
      expect(mockContext.setSelectedFile).toHaveBeenCalledWith(null)
      expect(mockContext.setAppState).toHaveBeenCalledWith('IDLE')
      expect(mockContext.setError).toHaveBeenCalledWith('')
    })

    it('should clear input value when valid file is selected', () => {
      // Arrange
      const validFile = new File(['test content'], 'test-video.mp4', {
        type: 'video/mp4',
        lastModified: Date.now(),
      })
      
      // Mock validation to return success
      mockValidateVideoFile.mockReturnValue({
        isValid: true,
      })
      
      // Act
      handleFileChangeLogic(validFile, mockContext, mockValidateVideoFile)
      
      // Assert
      expect(mockContext.setInputValue).toHaveBeenCalledWith('')
    })
  })
})