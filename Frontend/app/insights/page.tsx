"use client"

import { useEffect, useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  AlertCircle,
  BarChart3,
  FileSpreadsheet,
  Loader2,
  Search,
} from "lucide-react"
import { apiClient, type HistorySummary } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date)
}

export default function InsightsLandingPage() {
  const { toast } = useToast()
  const router = useRouter()

  const [completedFiles, setCompletedFiles] = useState<HistorySummary[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const filteredFiles = useMemo(() => {
    const query = searchQuery.toLowerCase().trim()
    if (!query) return completedFiles

    return completedFiles.filter((item) => {
      const original = item.original_file_name.toLowerCase()
      const processed = (item.processed_file_name || "").toLowerCase()
      return original.includes(query) || processed.includes(query)
    })
  }, [completedFiles, searchQuery])

  useEffect(() => {
    const fetchCompletedFiles = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const response = await apiClient.getCompletedFiles(200, 0, false)
        setCompletedFiles(response.data)
      } catch (error: any) {
        console.error("Failed to load completed files:", error)
        setError(error.message || "Failed to load completed files")
        toast({
          title: "Error",
          description: "Failed to load completed files for insights",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchCompletedFiles()
  }, [toast])

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Insights</h1>
          <p className="text-muted-foreground mt-1">
            Select one completed file to open its dedicated analytics view
          </p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <CardTitle>Processed Files</CardTitle>
                <CardDescription>
                  Choose a file to open pro-level insights
                </CardDescription>
              </div>
              <div className="relative w-full sm:w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-center space-y-3">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Loading completed files...</p>
                </div>
              </div>
            ) : error ? (
              <div className="p-6">
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              </div>
            ) : filteredFiles.length === 0 ? (
              <div className="text-center py-12 space-y-3">
                <FileSpreadsheet className="h-8 w-8 mx-auto text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  {searchQuery ? "No matching completed files found" : "No completed files available yet"}
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>File</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Insights</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredFiles.map((file) => (
                      <TableRow key={file.history_id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
                              <FileSpreadsheet className="h-5 w-5 text-muted-foreground" />
                            </div>
                            <div>
                              <p className="font-medium">{file.original_file_name}</p>
                              {file.processed_file_name && (
                                <p className="text-xs text-muted-foreground">{file.processed_file_name}</p>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-muted-foreground">{formatDate(file.created_at)}</TableCell>
                        <TableCell>
                          <Badge>{file.status}</Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            size="sm"
                            onClick={() => router.push(`/insights/${file.history_id}`)}
                          >
                            <BarChart3 className="mr-2 h-4 w-4" />
                            Open Insights
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
