"use client"

import { useState } from "react"
import { apiClient } from "@/lib/api-client"
import { useAuth } from "@/context/auth-context"

interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

interface PreprocessingReport {
  missing_values: number
  duplicate_rows: number
  cleaned_rows: number
  // Add more fields as per your backend response
}

interface Analytics {
  row_count: number
  column_count: number
  // Add more fields as per your backend response
}

interface UploadResult {
  message: string
  user_id: string
  preprocessing_report: PreprocessingReport
  analytics: Analytics
}

export function useFileUpload() {
  const { isAuthenticated } = useAuth()
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null)
  const [error, setError] = useState<string | null>(null)

  const uploadFile = async (file: File): Promise<UploadResult> => {
    if (!isAuthenticated) {
      throw new Error("You must be logged in to upload files")
    }

    setIsUploading(true)
    setError(null)
    setUploadProgress({ loaded: 0, total: file.size, percentage: 0 })

    try {
      // Simulate progress for user feedback
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (!prev) return null
          const newPercentage = Math.min(prev.percentage + 10, 90)
          return {
            ...prev,
            percentage: newPercentage,
          }
        })
      }, 200)

      const result = await apiClient.uploadDataset(file)

      clearInterval(progressInterval)
      setUploadProgress({ loaded: file.size, total: file.size, percentage: 100 })

      return result
    } catch (err: any) {
      setError(err.message || "Failed to upload file. Please try again.")
      throw err
    } finally {
      setIsUploading(false)
      setTimeout(() => setUploadProgress(null), 1000)
    }
  }

  const reset = () => {
    setError(null)
    setUploadProgress(null)
    setIsUploading(false)
  }

  return {
    uploadFile,
    isUploading,
    uploadProgress,
    error,
    reset,
  }
}
