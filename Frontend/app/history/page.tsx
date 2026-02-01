"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  FileSpreadsheet,
  Download,
  BarChart3,
  MoreVertical,
  Search,
  Trash2,
  Calendar,
  HardDrive,
  Loader2,
  AlertCircle,
} from "lucide-react"
import Link from "next/link"
import { apiClient, type HistorySummary } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"


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

export default function HistoryPage() {
  const { toast } = useToast()
  
  const [searchQuery, setSearchQuery] = useState("")
  const [historyData, setHistoryData] = useState<HistorySummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  
  const [stats, setStats] = useState({
    totalFiles: 0,
    processedFiles: 0,
    totalRows: 0,
  })

  // Fetch history data
  useEffect(() => {
    fetchHistory()
    fetchStats()
  }, [])

  const fetchHistory = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getHistory(100, 0)
      setHistoryData(response.data)
    } catch (error: any) {
      console.error("Failed to fetch history:", error)
      setError(error.message || "Failed to load history")
      toast({
        title: "Error",
        description: "Failed to load history data",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await apiClient.getHistoryStats()
      setStats({
        totalFiles: response.data.total_records,
        processedFiles: response.data.successful_processings,
        totalRows: 0, // Backend doesn't provide this yet
      })
    } catch (error) {
      console.error("Failed to fetch stats:", error)
    }
  }

  const handleDelete = async (historyId: string) => {
    setDeletingId(historyId)
    setDeleteDialogOpen(true)
  }

  const confirmDelete = async () => {
    if (!deletingId) return

    setIsDeleting(true)
    
    try {
      await apiClient.deleteHistory(deletingId, true)
      
      // Remove from local state
      setHistoryData(prev => prev.filter(item => item.history_id !== deletingId))
      
      toast({
        title: "Success",
        description: "History record deleted successfully",
      })
      
      // Refresh stats
      fetchStats()
    } catch (error: any) {
      console.error("Failed to delete:", error)
      toast({
        title: "Error",
        description: error.message || "Failed to delete record",
        variant: "destructive",
      })
    } finally {
      setIsDeleting(false)
      setDeleteDialogOpen(false)
      setDeletingId(null)
    }
  }

  const handleDownload = async (historyId: string) => {
    try {
      const response = await apiClient.getHistoryDetail(historyId)
      
      if (response.data.processed_file?.download_url) {
        window.open(response.data.processed_file.download_url, '_blank')
        toast({
          title: "Download Started",
          description: "Your file is being downloaded",
        })
      } else {
        toast({
          title: "Not Available",
          description: "Processed file is not available for this record",
          variant: "destructive",
        })
      }
    } catch (error: any) {
      console.error("Failed to get download link:", error)
      toast({
        title: "Error",
        description: "Failed to start download",
        variant: "destructive",
      })
    }
  }

  const filteredData = historyData.filter((item) =>
    item.original_file_name.toLowerCase().includes(searchQuery.toLowerCase())
  )


  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">History</h1>
            <p className="text-muted-foreground mt-1">
              View and manage your previously uploaded datasets
            </p>
          </div>
          <Button asChild>
            <Link href="/upload">Upload New</Link>
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Uploads
              </CardTitle>
              <FileSpreadsheet className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalFiles}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stats.processedFiles} processed
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Rows
              </CardTitle>
              <HardDrive className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalRows || '-'}</div>
              <p className="text-xs text-muted-foreground mt-1">Across all datasets</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Last Upload
              </CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {historyData.length > 0 ? formatDate(historyData[0].created_at).split(',')[0] : '-'}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {historyData.length > 0 ? formatDate(historyData[0].created_at).split(',')[1] : 'No uploads yet'}
              </p>
            </CardContent>
          </Card>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Search and Table */}
        <Card>
          <CardHeader>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <CardTitle>Upload History</CardTitle>
                <CardDescription>
                  All your uploaded and processed datasets
                </CardDescription>
              </div>
              <div className="relative w-full sm:w-72">
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
                  <p className="text-sm text-muted-foreground">Loading history...</p>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>File Name</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredData.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-8">
                          <p className="text-muted-foreground">
                            {searchQuery ? 'No files found' : 'No upload history yet'}
                          </p>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredData.map((item) => (
                        <TableRow key={item.history_id}>
                          <TableCell>
                            <div className="flex items-center gap-3">
                              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
                                <FileSpreadsheet className="h-5 w-5 text-muted-foreground" />
                              </div>
                              <div>
                                <span className="font-medium block">{item.original_file_name}</span>
                                {item.processed_file_name && (
                                  <span className="text-xs text-muted-foreground">
                                    → {item.processed_file_name}
                                  </span>
                                )}
                              </div>
                            </div>
                          </TableCell>
                          <TableCell className="capitalize">
                            {item.file_type}
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {formatDate(item.created_at)}
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={item.status === "success" ? "default" : item.status === "failed" ? "destructive" : "secondary"}
                            >
                              {item.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" className="h-8 w-8">
                                  <MoreVertical className="h-4 w-4" />
                                  <span className="sr-only">Open menu</span>
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem
                                  onClick={() => handleDownload(item.history_id)}
                                  disabled={item.status !== "success"}
                                >
                                  <Download className="mr-2 h-4 w-4" />
                                  Download
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  onClick={() => handleDelete(item.history_id)}
                                  className="text-destructive"
                                >
                                  <Trash2 className="mr-2 h-4 w-4" />
                                  Delete
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you sure?</AlertDialogTitle>
              <AlertDialogDescription>
                This will permanently delete this history record and the associated files from storage.
                This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={confirmDelete}
                disabled={isDeleting}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                {isDeleting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  'Delete'
                )}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </DashboardLayout>
  )
}
