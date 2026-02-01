"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { FileUpload } from "@/components/dashboard/file-upload"
import { DataTablePreview } from "@/components/dashboard/data-table-preview"
import { StatsCards } from "@/components/dashboard/stats-cards"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Loader2, Download, Wand2, CheckCircle, AlertCircle } from "lucide-react"
import { apiClient, type PreprocessingConfig, type UploadResponse } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

// Parse CSV/Excel to preview data
function parseFileForPreview(file: File): Promise<{
  data: Record<string, unknown>[]
  columns: string[]
}> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      try {
        const text = e.target?.result as string
        const lines = text.split('\n').filter(line => line.trim())
        
        if (lines.length === 0) {
          reject(new Error('File is empty'))
          return
        }
        
        // Parse CSV header
        const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
        
        // Parse rows (limit to first 20 for preview)
        const data: Record<string, unknown>[] = []
        const previewLines = lines.slice(1, Math.min(21, lines.length))
        
        previewLines.forEach((line, idx) => {
          const values = line.split(',').map(v => v.trim().replace(/"/g, ''))
          const row: Record<string, unknown> = {}
          
          headers.forEach((header, i) => {
            const value = values[i] || ''
            // Try to parse as number
            const numValue = parseFloat(value)
            row[header] = !isNaN(numValue) && value !== '' ? numValue : value
          })
          
          data.push(row)
        })
        
        resolve({ data, columns: headers })
      } catch (error) {
        reject(error)
      }
    }
    
    reader.onerror = () => reject(new Error('Failed to read file'))
    reader.readAsText(file)
  })
}

function calculateStats(data: Record<string, unknown>[], columns: string[]) {
  let missingValues = 0
  const rowStrings = new Set<string>()
  let duplicates = 0

  data.forEach((row) => {
    const rowString = JSON.stringify(row)
    if (rowStrings.has(rowString)) {
      duplicates++
    } else {
      rowStrings.add(rowString)
    }

    columns.forEach((col) => {
      if (row[col] === null || row[col] === undefined || row[col] === "") {
        missingValues++
      }
    })
  })

  return {
    rowCount: data.length,
    columnCount: columns.length,
    missingValues,
    duplicateRows: duplicates,
  }
}


export default function UploadPage() {
  const router = useRouter()
  const { toast } = useToast()
  
  const [file, setFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isProcessed, setIsProcessed] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  
  const [parsedData, setParsedData] = useState<{
    data: Record<string, unknown>[]
    columns: string[]
  } | null>(null)
  
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null)

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile)
    setIsLoading(true)
    setIsProcessed(false)
    setError(null)
    setParsedData(null)
    setUploadResult(null)

    try {
      // Parse file for preview
      const result = await parseFileForPreview(selectedFile)
      setParsedData(result)
    } catch (error: any) {
      console.error("Error parsing file:", error)
      setError(error.message || "Failed to parse file")
      toast({
        title: "Error",
        description: "Failed to preview file. You can still try to process it.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handlePreprocess = async () => {
    if (!file) return

    setIsProcessing(true)
    setProgress(0)
    setError(null)

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 500)

      // Preprocessing configuration (can be made customizable)
      const config: PreprocessingConfig = {
        missing_threshold: 50.0,
        outlier_method: 'cap',
        cardinality_threshold: 10,
        scaling_method: 'auto',
      }

      const response = await apiClient.uploadDataset(file, config)
      
      clearInterval(progressInterval)
      setProgress(100)
      
      setUploadResult(response)
      
      if (response.status === 'success') {
        setIsProcessed(true)
        toast({
          title: "Success!",
          description: "Dataset processed successfully",
        })
      } else if (response.status === 'error') {
        setError(response.message || "Processing failed")
        toast({
          title: "Processing Error",
          description: response.message,
          variant: "destructive",
        })
      }
      
    } catch (error: any) {
      console.error("Upload error:", error)
      setError(error.message || "Failed to process file")
      toast({
        title: "Error",
        description: error.message || "Failed to process file",
        variant: "destructive",
      })
    } finally {
      setIsProcessing(false)
    }
  }

  const handleDownload = () => {
    if (uploadResult?.processed_file_url) {
      // Open download link in new tab
      window.open(uploadResult.processed_file_url, '_blank')
      toast({
        title: "Download Started",
        description: "Your processed file is being downloaded",
      })
    }
  }

  const handleViewHistory = () => {
    router.push('/history')
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Upload Dataset</h1>
          <p className="text-muted-foreground mt-1">
            Upload your CSV or Excel file to start preprocessing
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Select File</CardTitle>
            <CardDescription>
              Drag and drop your dataset or click to browse
            </CardDescription>
          </CardHeader>
          <CardContent>
            <FileUpload onFileSelect={handleFileSelect} />
          </CardContent>
        </Card>

        {error && !isProcessing && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {isLoading && (
          <Card>
            <CardContent className="flex items-center justify-center py-12">
              <div className="text-center space-y-3">
                <Loader2 className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Parsing your file...</p>
              </div>
            </CardContent>
          </Card>
        )}

        {parsedData && !isLoading && (
          <>
            <StatsCards stats={calculateStats(parsedData.data, parsedData.columns)} />

            <DataTablePreview
              data={parsedData.data}
              columns={parsedData.columns}
              maxRows={10}
            />

            <Card>
              <CardHeader>
                <CardTitle>Preprocessing Actions</CardTitle>
                <CardDescription>
                  Run AI-powered preprocessing to clean and prepare your data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {isProcessing && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Processing...</span>
                      <span className="font-medium">{progress}%</span>
                    </div>
                    <Progress value={progress} />
                    <p className="text-xs text-muted-foreground">
                      Cleaning data, handling missing values, encoding features...
                    </p>
                  </div>
                )}

                {isProcessed && uploadResult?.status === 'success' && (
                  <Alert>
                    <CheckCircle className="h-4 w-4" />
                    <AlertTitle>Success!</AlertTitle>
                    <AlertDescription>
                      {uploadResult.message || 'Preprocessing complete! Your data is ready for download.'}
                    </AlertDescription>
                  </Alert>
                )}

                {uploadResult?.preprocessing_report && (
                  <Card className="bg-muted/50">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">Preprocessing Summary</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      {uploadResult.preprocessing_report.original_shape && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Original Shape:</span>
                          <span className="font-mono">
                            {uploadResult.preprocessing_report.original_shape.join(' × ')}
                          </span>
                        </div>
                      )}
                      {uploadResult.preprocessing_report.processed_shape && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Processed Shape:</span>
                          <span className="font-mono">
                            {uploadResult.preprocessing_report.processed_shape.join(' × ')}
                          </span>
                        </div>
                      )}
                      {uploadResult.preprocessing_report.missing_values_handled !== undefined && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Missing Values Handled:</span>
                          <span className="font-medium">
                            {uploadResult.preprocessing_report.missing_values_handled}
                          </span>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}

                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    onClick={handlePreprocess}
                    disabled={isProcessing || isProcessed}
                    className="flex-1"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : isProcessed ? (
                      <>
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Processed
                      </>
                    ) : (
                      <>
                        <Wand2 className="mr-2 h-4 w-4" />
                        Preprocess Data
                      </>
                    )}
                  </Button>

                  <Button
                    variant="outline"
                    onClick={handleDownload}
                    disabled={!isProcessed || !uploadResult?.processed_file_url}
                    className="flex-1 bg-transparent"
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download Cleaned File
                  </Button>
                </div>

                {isProcessed && (
                  <Button
                    variant="secondary"
                    onClick={handleViewHistory}
                    className="w-full"
                  >
                    View in History
                  </Button>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </DashboardLayout>
  )
}
