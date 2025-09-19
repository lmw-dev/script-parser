/**
 * Smart progress algorithm for processing page
 * Implements three-stage progress with easing functions
 * Based on TOM-319 PRD requirements
 */

import { useState, useEffect } from 'react'

export interface ProgressConfig {
  totalDuration: number // 48 seconds
  stages: {
    name: string
    duration: number
    startProgress: number
    endProgress: number
    easing: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out'
  }[]
}

export const progressConfig: ProgressConfig = {
  totalDuration: 48000, // 48 seconds
  stages: [
    {
      name: "(1/3) 正在安全上传并解析视频...",
      duration: 5000,    // 0-5 seconds
      startProgress: 0,
      endProgress: 20,
      easing: 'ease-out'
    },
    {
      name: "(2/3) 正在调用ASR服务，提取高质量逐字稿...",
      duration: 35000,   // 5-40 seconds
      startProgress: 20,
      endProgress: 80,
      easing: 'linear'
    },
    {
      name: "(3/3) 正在调用LLM，进行AI结构化分析...",
      duration: 8000,    // 40-48 seconds
      startProgress: 80,
      endProgress: 99,
      easing: 'ease-in'
    }
  ]
}

/**
 * Apply easing function to progress value
 */
function applyEasing(progress: number, easing: string): number {
  switch (easing) {
    case 'linear':
      return progress
    case 'ease-in':
      return progress * progress
    case 'ease-out':
      return 1 - Math.pow(1 - progress, 2)
    case 'ease-in-out':
      return progress < 0.5 
        ? 2 * progress * progress 
        : 1 - Math.pow(-2 * progress + 2, 2) / 2
    default:
      return progress
  }
}

/**
 * Calculate progress based on elapsed time
 * Returns current progress percentage and stage index
 */
export function calculateProgress(elapsedTime: number): { 
  progress: number
  currentStage: number
  stageName: string
} {
  let cumulativeTime = 0
  
  for (let i = 0; i < progressConfig.stages.length; i++) {
    const stage = progressConfig.stages[i]
    
    if (elapsedTime <= cumulativeTime + stage.duration) {
      // We're in this stage
      const stageElapsed = elapsedTime - cumulativeTime
      const stageProgress = stageElapsed / stage.duration
      const easedProgress = applyEasing(stageProgress, stage.easing)
      const progress = stage.startProgress + (stage.endProgress - stage.startProgress) * easedProgress
      
      return { 
        progress: Math.min(progress, 99), 
        currentStage: i + 1,
        stageName: stage.name
      }
    }
    
    cumulativeTime += stage.duration
  }
  
  // If we've exceeded all stages, return the final stage
  const finalStage = progressConfig.stages[progressConfig.stages.length - 1]
  return { 
    progress: 99, 
    currentStage: progressConfig.stages.length,
    stageName: finalStage.name
  }
}

/**
 * Hook for managing progress animation
 */
export function useProgressAnimation(
  onComplete: () => void,
  apiCompleted: boolean = false
) {
  const [progress, setProgress] = useState(0)
  const [currentStage, setCurrentStage] = useState(1)
  const [stageName, setStageName] = useState(progressConfig.stages[0].name)
  const [startTime] = useState(Date.now())

  useEffect(() => {
    if (apiCompleted) {
      // API completed, immediately set to 100% and trigger completion
      setProgress(100)
      setTimeout(() => onComplete(), 500) // Small delay for smooth transition
      return
    }

    const updateProgress = () => {
      const elapsedTime = Date.now() - startTime
      const { progress: newProgress, currentStage: newStage, stageName: newStageName } = calculateProgress(elapsedTime)
      
      setProgress(newProgress)
      setCurrentStage(newStage)
      setStageName(newStageName)
      
      // If progress reaches 99%, stop updating and wait for API
      if (newProgress >= 99) {
        return
      }
      
      // Continue animation
      requestAnimationFrame(updateProgress)
    }

    const animationId = requestAnimationFrame(updateProgress)
    return () => cancelAnimationFrame(animationId)
  }, [startTime, onComplete, apiCompleted])

  return { progress, currentStage, stageName }
}
