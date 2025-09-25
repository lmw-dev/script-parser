/**
 * InputSection component - handles URL and file input
 * Based on TOM-318 and TOM-323 specifications
 * Refactored as a controlled component
 */

"use client"

import type React from "react"
import { useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
// File validation is now handled by the parent component
import type { InputSectionProps } from "@/types/script-parser.types"
import { Upload, Link, Sparkles, X } from "lucide-react"

export function InputSection({ 
  currentState, 
  inputValue, 
  selectedFile, 
  onInputChange, 
  onFileSelect, 
  onSubmit, 
  error 
}: InputSectionProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  const handleInputChange = (value: string) => {
    // Clear file when URL is being entered
    if (selectedFile) {
      onFileSelect(null)
    }
    onInputChange(value)
  }

  const handleFileUpload = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null
    
    // Pass the file to parent component for validation and state management
    onFileSelect(file)
    
    // Reset the input so the same file can be selected again if needed
    if (event.target) {
      event.target.value = ''
    }
    
    // Show success toast only for valid files (parent will handle errors)
    if (file && !error) {
      toast({
        title: "文件已选择",
        description: `${file.name} (${(file.size / 1024 / 1024).toFixed(1)}MB)`,
        duration: 3000,
      })
    }
  }

  const isSubmitDisabled = currentState === "IDLE" || currentState === "PROCESSING"

  return (
    <div className="w-full max-w-2xl space-y-6">
      <div className="bg-card/80 backdrop-blur-sm border border-border rounded-2xl md:rounded-3xl shadow-xl p-6 md:p-12 space-y-6">
        <div className="text-center space-y-2 md:space-y-4">
          <h2 className="text-xl md:text-2xl font-semibold text-foreground">开始分析你的视频</h2>
          <p className="text-sm md:text-base text-muted-foreground">粘贴链接或上传文件，让AI为你解析脚本结构</p>
        </div>

        <div className="space-y-4">
          <div className="relative group">
            <Link className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              placeholder="在此处粘贴抖音/小红书分享链接..."
              value={selectedFile ? `本地文件: ${selectedFile.name}` : inputValue}
              onChange={(e) => handleInputChange(e.target.value)}
              disabled={!!selectedFile || currentState === "PROCESSING"}
              className="bg-input border border-border rounded-xl px-4 py-4 pl-12 h-14 md:h-16 text-center text-base md:text-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-all duration-200 disabled:text-foreground disabled:cursor-default"
            />
            {selectedFile && currentState !== "PROCESSING" && (
              <button 
                onClick={() => onFileSelect(null)}
                className="absolute right-4 top-1/2 transform -translate-y-1/2 h-6 w-6 bg-muted rounded-full flex items-center justify-center text-muted-foreground hover:bg-destructive hover:text-destructive-foreground transition-all duration-200 opacity-0 group-hover:opacity-100"
                aria-label="Clear file"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-center">
              <p className="text-sm text-destructive font-medium">{error}</p>
            </div>
          )}
        </div>

        <Button
          onClick={onSubmit}
          disabled={isSubmitDisabled}
          className="bg-primary text-primary-foreground px-8 py-4 rounded-xl font-semibold w-full h-14 md:h-16 text-base md:text-lg transition-all duration-200 hover:bg-primary/90 hover:shadow-lg hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 shadow-lg"
          size="lg"
        >
          {currentState === "PROCESSING" ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3" />
              处理中...
            </>
          ) : (
            <>
              <Sparkles className="h-5 w-5 mr-3" />
              开始分析
            </>
          )}
        </Button>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-border" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-card px-2 text-muted-foreground font-medium">或者</span>
          </div>
        </div>

        <Button
          variant="outline"
          onClick={handleFileUpload}
          disabled={currentState === "PROCESSING"}
          className="w-full h-14 md:h-16 border-2 border-dashed border-primary/30 bg-primary/5 hover:bg-primary/10 hover:border-primary/50 rounded-xl transition-all duration-300 text-base md:text-lg font-medium"
        >
          <Upload className="h-5 w-5 md:h-6 md:w-6 mr-3 text-primary" />
          <span className="text-foreground">上传本地视频文件</span>
        </Button>

        <p className="text-xs text-muted-foreground text-center">
          支持 MP4, MOV, AVI, WEBM 等格式，文件大小不超过 100MB。
        </p>
      </div>

      <input ref={fileInputRef} type="file" accept="video/*" onChange={handleFileChange} className="hidden" />
    </div>
  )
}
