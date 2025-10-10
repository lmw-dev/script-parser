"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useToast } from "@/hooks/use-toast"
import { InputSection } from "@/components/sections/InputSection"
import { extractAndValidateUrl, validateVideoFile } from "@/lib/validation"
import { useAppStore } from "@/stores/app-store"
import type { VideoParseRequest } from "@/types/script-parser.types"
import { Sparkles, FileText, Zap } from "lucide-react"

export default function HomePage() {
  const router = useRouter()
  const { toast } = useToast()
  const { startProcessing } = useAppStore()
  
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
    startProcessing(request)
    router.push('/processing')
  }

  return (
    <div className="flex-grow flex flex-col lg:flex-row">
      <div className="w-full lg:w-2/5 bg-gradient-to-br from-primary/5 to-primary/10 border-b lg:border-b-0 lg:border-r border-border flex flex-col justify-center p-6 lg:p-12">
        <div className="space-y-6">
          <div className="space-y-4">
            <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20">
              <div className="w-1.5 h-1.5 bg-primary rounded-full" />
              <span className="text-xs font-medium text-foreground/70 uppercase tracking-wide">AI Analysis</span>
            </div>
            <h1 className="text-3xl lg:text-5xl font-bold text-gradient-linear tracking-tight leading-tight">
              AI 脚本快拆
            </h1>
            <p className="text-base lg:text-lg text-muted-foreground leading-relaxed">
              专业级视频脚本分析工具，一键提取逐字稿并进行AI结构化分析
            </p>
          </div>

          <div className="space-y-4">
            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">AI 智能分析</h3>
                <p className="text-sm text-muted-foreground">先进的AI算法，精准提取脚本结构</p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                <FileText className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">多格式支持</h3>
                <p className="text-sm text-muted-foreground">支持主流视频平台链接和本地文件</p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                <Zap className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">快速处理</h3>
                <p className="text-sm text-muted-foreground">秒级响应，高效完成分析任务</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center p-6 lg:p-12">
        <div className="text-center mb-10">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 dark:text-gray-100 tracking-tight">
            AI 脚本快拆
          </h1>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400 max-w-xl">
            粘贴视频链接，即刻获取AI结构化分析脚本，让你的内容创作效率倍增。
          </p>
        </div>
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
  )
}