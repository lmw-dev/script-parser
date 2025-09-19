"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useToast } from "@/hooks/use-toast"
import { InputSection } from "@/components/sections/InputSection"
import { extractAndValidateUrl, validateVideoFile } from "@/lib/validation"
import { useAnalysisStore } from "@/stores/analysis-store"
import type { VideoParseRequest } from "@/types/script-parser.types"
import { Sparkles, FileText, Zap } from "lucide-react"

export default function HomePage() {
  const router = useRouter()
  const { toast } = useToast()
  const { setInputData } = useAnalysisStore()
  
  // Local state for input validation only
  const [inputValue, setInputValue] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isValid, setIsValid] = useState(false)
  const [error, setError] = useState("")

  // Handle input change with URL extraction and validation
  const handleInputChange = (value: string) => {
    setInputValue(value)
    setError("")
    
    // Clear file when URL is being entered
    if (selectedFile) {
      setSelectedFile(null)
    }
    
    // Update validation state
    if (value.trim() === "") {
      setIsValid(false)
      return
    }

    const validationResult = extractAndValidateUrl(value)
    setIsValid(validationResult.isValid)
    
    if (!validationResult.isValid) {
      setError(validationResult.error || "请输入有效的视频链接")
    }
  }

  // Handle file selection
  const handleFileSelect = (file: File | null) => {
    setSelectedFile(file)
    setError("")
    
    // Clear URL input when file is selected
    if (file) {
      setInputValue("")
    }
    
    if (!file) {
      setIsValid(false)
      return
    }

    // Validate the selected file
    const validationResult = validateVideoFile(file)
    setIsValid(validationResult.isValid)
    
    if (!validationResult.isValid) {
      setError(validationResult.error || "文件验证失败")
    } else {
      toast({
        title: "文件已选择",
        description: `${file.name} (${(file.size / 1024 / 1024).toFixed(1)}MB)`,
        duration: 3000,
      })
    }
  }

  // Handle form submission - navigate to processing page
  const handleSubmit = () => {
    if (!isValid) {
      setError("请先输入有效的视频链接或选择文件")
      return
    }

    // Prepare data for submission
    let request: VideoParseRequest
    
    if (selectedFile) {
      request = { 
        type: 'file',
        url: '',
        file: selectedFile 
      }
    } else if (inputValue.trim()) {
      const validationResult = extractAndValidateUrl(inputValue)
      
      if (validationResult.isValid && validationResult.extractedUrl) {
        request = { 
          type: 'url',
          url: validationResult.extractedUrl,
          file: null 
        }
      } else {
        setError(validationResult.error || "请输入有效的视频链接")
        return
      }
    } else {
      setError("请输入视频链接或选择文件")
      return
    }

    // Store data in Zustand store and navigate
    setInputData(request)
    router.push('/processing')
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="h-14 bg-primary border-b border-primary/20 flex items-center justify-between px-6">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-white/20 rounded flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="text-white font-semibold text-sm">AI 脚本快拆</span>
            <span className="text-white/60 text-xs">by v0</span>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-3 py-1.5 bg-black/30 hover:bg-black/40 text-white text-xs font-medium rounded-md transition-colors border border-white/10">
            开始使用
          </button>
          <button className="px-3 py-1.5 bg-white text-primary text-xs font-medium rounded-md hover:bg-white/90 transition-colors">
            立即体验
          </button>
        </div>
      </div>

      <div className="h-[calc(100vh-3.5rem)] flex">
        <div className="w-2/5 bg-gradient-to-br from-primary/5 to-primary/10 border-r border-border flex flex-col justify-center px-12">
          <div className="space-y-8">
            <div className="space-y-6">
              <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20">
                <div className="w-1.5 h-1.5 bg-primary rounded-full" />
                <span className="text-xs font-medium text-foreground/70 uppercase tracking-wide">AI Analysis</span>
              </div>
              <h1 className="text-4xl lg:text-5xl font-bold text-gradient-linear tracking-tight leading-tight">
                AI 脚本快拆
              </h1>
              <p className="text-lg text-muted-foreground leading-relaxed">
                专业级视频脚本分析工具，一键提取逐字稿并进行AI结构化分析
              </p>
            </div>

            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">AI 智能分析</h3>
                  <p className="text-sm text-muted-foreground">先进的AI算法，精准提取脚本结构</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                  <FileText className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">多格式支持</h3>
                  <p className="text-sm text-muted-foreground">支持主流视频平台链接和本地文件</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Zap className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">快速处理</h3>
                  <p className="text-sm text-muted-foreground">秒级响应，高效完成分析任务</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1 flex items-center justify-center px-12">
          <InputSection 
            currentState={isValid ? "INPUT_VALID" : "IDLE"}
            inputValue={inputValue}
            selectedFile={selectedFile}
            onInputChange={handleInputChange}
            onFileSelect={handleFileSelect}
            onSubmit={handleSubmit}
            error={error}
          />
        </div>
      </div>
    </div>
  )
}