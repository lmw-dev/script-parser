/**
 * InputSection component - handles URL and file input
 * Based on TOM-318 specification
 */

"use client"

import type React from "react"
import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { isValidUrl, validateVideoFile } from "@/lib/validation"
import type { InputSectionProps, VideoParseRequest } from "@/types/script-parser.types"
import { Upload, Link, Sparkles } from "lucide-react"

export function InputSection({ onSubmit, onStateChange, currentState, error }: InputSectionProps) {
  const [inputUrl, setInputUrl] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  const handleInputChange = (value: string) => {
    setInputUrl(value)
    setSelectedFile(null) // Clear file when URL is entered

    if (value.trim() && isValidUrl(value)) {
      onStateChange("INPUT_VALID")
    } else {
      onStateChange("IDLE")
    }
  }

  const handleFileUpload = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const validation = validateVideoFile(file)
    if (!validation.isValid) {
      onStateChange("ERROR")
      return
    }

    setSelectedFile(file)
    setInputUrl("") // Clear URL when file is selected
    onStateChange("INPUT_VALID")

    toast({
      title: "文件已选择",
      description: `${file.name} (${(file.size / 1024 / 1024).toFixed(1)}MB)`,
      duration: 3000,
    })
  }

  const handleSubmit = () => {
    const data: VideoParseRequest = {}

    if (inputUrl) {
      data.url = inputUrl
    } else if (selectedFile) {
      data.file = selectedFile
    }

    onSubmit(data)
  }

  const isSubmitDisabled = currentState === "IDLE" || currentState === "PROCESSING"

  return (
    <div className="w-full max-w-2xl space-y-8">
      <div className="bg-card/80 backdrop-blur-sm border border-border rounded-3xl shadow-xl p-12 space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-semibold text-foreground">开始分析你的视频</h2>
          <p className="text-muted-foreground">粘贴链接或上传文件，让AI为你解析脚本结构</p>
        </div>

        <div className="space-y-6">
          <div className="relative">
            <Link className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              placeholder="在此处粘贴抖音/小红书分享链接..."
              value={selectedFile ? `本地文件: ${selectedFile.name}` : inputUrl}
              onChange={(e) => handleInputChange(e.target.value)}
              disabled={!!selectedFile || currentState === "PROCESSING"}
              className="bg-input border border-border rounded-xl px-4 py-4 pl-12 h-16 text-center text-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-all duration-200"
            />
          </div>

          {error && currentState === "ERROR" && (
            <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/20">
              <p className="text-sm text-destructive font-medium">{error}</p>
            </div>
          )}
        </div>

        <Button
          onClick={handleSubmit}
          disabled={isSubmitDisabled}
          className="bg-primary text-primary-foreground px-8 py-4 rounded-xl font-semibold w-full h-16 text-lg transition-all duration-200 hover:bg-primary/90 hover:shadow-lg hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 shadow-lg"
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
          <div className="relative flex justify-center text-sm uppercase">
            <span className="bg-card px-4 text-muted-foreground font-medium">或者</span>
          </div>
        </div>

        <Button
          variant="outline"
          onClick={handleFileUpload}
          disabled={currentState === "PROCESSING"}
          className="w-full h-16 border-2 border-dashed border-primary/30 bg-primary/5 hover:bg-primary/10 hover:border-primary/50 rounded-xl transition-all duration-300 text-lg font-medium"
        >
          <Upload className="h-6 w-6 mr-3 text-primary" />
          <span className="text-foreground">上传本地视频文件</span>
        </Button>
      </div>

      <input ref={fileInputRef} type="file" accept="video/*" onChange={handleFileChange} className="hidden" />
    </div>
  )
}
