"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { FileUpload } from "@/components/dashboard/file-upload"
import { DataTablePreview } from "@/components/dashboard/data-table-preview"
import { StatsCards } from "@/components/dashboard/stats-cards"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Loader2, Download, Wand2, CheckCircle } from "lucide-react"

// Mock data parser - in production, this would parse actual CSV/Excel files
function parseFile(file: File): Promise<{
  data: Record<string, unknown>[]
  columns: string[]
}> {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Mock parsed data
      const mockData = [
        { id: 1, name: "John Doe", age: 28, email: "john@example.com", salary: 75000, department: "Engineering" },
        { id: 2, name: "Jane Smith", age: 34, email: "jane@example.com", salary: 82000, department: "Marketing" },
        { id: 3, name: "Bob Wilson", age: null, email: "bob@example.com", salary: 65000, department: "Sales" },
        { id: 4, name: "Alice Brown", age: 29, email: null, salary: 78000, department: "Engineering" },
        { id: 5, name: "Charlie Davis", age: 45, email: "charlie@example.com", salary: 95000, department: "Management" },
        { id: 6, name: "Eva Martinez", age: 31, email: "eva@example.com", salary: null, department: "Marketing" },
        { id: 7, name: "Frank Lee", age: 38, email: "frank@example.com", salary: 72000, department: "Sales" },
        { id: 8, name: "Grace Kim", age: 26, email: "grace@example.com", salary: 68000, department: "Engineering" },
        { id: 9, name: "Henry Chen", age: null, email: "henry@example.com", salary: 85000, department: "Engineering" },
        { id: 10, name: "Ivy Wong", age: 33, email: "ivy@example.com", salary: 79000, department: "Marketing" },
        { id: 11, name: "Jack Brown", age: 41, email: null, salary: 91000, department: "Management" },
        { id: 12, name: "Karen White", age: 29, email: "karen@example.com", salary: 74000, department: "Sales" },
      ]
      const columns = ["id", "name", "age", "email", "salary", "department"]
      resolve({ data: mockData, columns })
    }, 1500)
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
  const [file, setFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isProcessed, setIsProcessed] = useState(false)
  const [progress, setProgress] = useState(0)
  const [parsedData, setParsedData] = useState<{
    data: Record<string, unknown>[]
    columns: string[]
  } | null>(null)

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile)
    setIsLoading(true)
    setIsProcessed(false)
    setParsedData(null)

    try {
      const result = await parseFile(selectedFile)
      setParsedData(result)
    } catch (error) {
      console.error("[v0] Error parsing file:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handlePreprocess = async () => {
    setIsProcessing(true)
    setProgress(0)

    // Simulate preprocessing steps
    const steps = [20, 40, 60, 80, 100]
    for (const step of steps) {
      await new Promise((resolve) => setTimeout(resolve, 600))
      setProgress(step)
    }

    setIsProcessing(false)
    setIsProcessed(true)
  }

  const handleDownload = () => {
    // In production, this would download the processed file
    const blob = new Blob([JSON.stringify(parsedData?.data, null, 2)], {
      type: "application/json",
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `processed_${file?.name || "data"}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
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
                  </div>
                )}

                {isProcessed && (
                  <div className="flex items-center gap-2 p-3 bg-success/10 text-success rounded-lg border border-success/20">
                    <CheckCircle className="h-5 w-5" />
                    <span className="font-medium">
                      Preprocessing complete! Your data is ready for download.
                    </span>
                  </div>
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
                    disabled={!isProcessed}
                    className="flex-1 bg-transparent"
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download Cleaned File
                  </Button>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </DashboardLayout>
  )
}
