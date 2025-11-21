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
  totalDuration: 90000, // 90 seconds (Extended to cover longer processing times)
  stages: [
    {
      name: "(1/3) 正在安全上传并解析视频...",
      duration: 4000,    // 0-4 seconds (Fast start)
      startProgress: 0,
      endProgress: 15,
      easing: 'ease-out'
    },
    {
      name: "(2/3) 正在调用ASR服务，提取高质量逐字稿...",
      duration: 30000,   // 4-34 seconds (Steady progress)
      startProgress: 15,
      endProgress: 50,
      easing: 'linear'
    },
    {
      name: "(3/3) 正在调用LLM，进行AI结构化分析...",
      duration: 56000,    // 34-90 seconds (Slow down gradually)
      startProgress: 50,
      endProgress: 95,    // Cap at 95% to avoid "stuck at 99%" feeling
      easing: 'ease-out'  // Decelerate to make it feel natural if it takes long
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
    let animationId: number;

    const updateProgress = () => {
      const elapsedTime = Date.now() - startTime
      const { progress: newProgress, currentStage: newStage, stageName: newStageName } = calculateProgress(elapsedTime)

      setProgress(newProgress)
      setCurrentStage(newStage)
      setStageName(newStageName)

      // If progress reaches 99%, stop the animation loop and wait for the API to complete.
      if (newProgress < 99) {
        animationId = requestAnimationFrame(updateProgress)
      }
    }

    if (apiCompleted) {
      // API has finished, so we stop any running animation.
      // The `cancelAnimationFrame` would be for an animationId set in a previous render.
      // Since we are re-running the effect, we just need to not start a new loop.
      setProgress(100)
      setTimeout(() => onComplete(), 500) // Small delay for smooth transition
    } else {
      // API is not complete, run the animation.
      animationId = requestAnimationFrame(updateProgress)
    }

    return () => {
      // Cleanup: cancel the animation frame when the component unmounts or dependencies change.
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
    }
  }, [startTime, onComplete, apiCompleted])

  return { progress, currentStage, stageName }
}
