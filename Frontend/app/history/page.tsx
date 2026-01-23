"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
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
} from "lucide-react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Suspense } from "react"

// Mock history data
const historyData = [
  {
    id: 1,
    fileName: "sales_data_2024.csv",
    originalSize: "2.4 MB",
    processedSize: "2.1 MB",
    rows: 15420,
    columns: 12,
    uploadDate: "2024-01-15T10:30:00",
    status: "processed",
  },
  {
    id: 2,
    fileName: "customer_segments.xlsx",
    originalSize: "1.8 MB",
    processedSize: "1.5 MB",
    rows: 8750,
    columns: 8,
    uploadDate: "2024-01-14T15:45:00",
    status: "processed",
  },
  {
    id: 3,
    fileName: "product_inventory.csv",
    originalSize: "5.2 MB",
    processedSize: "4.8 MB",
    rows: 32100,
    columns: 15,
    uploadDate: "2024-01-13T09:15:00",
    status: "processed",
  },
  {
    id: 4,
    fileName: "employee_records.xlsx",
    originalSize: "890 KB",
    processedSize: "820 KB",
    rows: 2450,
    columns: 10,
    uploadDate: "2024-01-12T14:20:00",
    status: "processed",
  },
  {
    id: 5,
    fileName: "marketing_metrics.csv",
    originalSize: "3.1 MB",
    processedSize: null,
    rows: 18900,
    columns: 20,
    uploadDate: "2024-01-11T11:00:00",
    status: "pending",
  },
  {
    id: 6,
    fileName: "financial_report_q4.xlsx",
    originalSize: "4.5 MB",
    processedSize: "4.2 MB",
    rows: 25600,
    columns: 18,
    uploadDate: "2024-01-10T16:30:00",
    status: "processed",
  },
]

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

function Loading() {
  return null
}

export default function HistoryPage() {
  const searchParams = useSearchParams()
  const [searchQuery, setSearchQuery] = useState("")

  const filteredData = historyData.filter((item) =>
    item.fileName.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const totalFiles = historyData.length
  const processedFiles = historyData.filter((f) => f.status === "processed").length
  const totalRows = historyData.reduce((acc, f) => acc + f.rows, 0)

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
              <div className="text-2xl font-bold">{totalFiles}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {processedFiles} processed
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
              <div className="text-2xl font-bold">{totalRows.toLocaleString()}</div>
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
              <div className="text-2xl font-bold">Today</div>
              <p className="text-xs text-muted-foreground mt-1">2 hours ago</p>
            </CardContent>
          </Card>
        </div>

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
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>File Name</TableHead>
                    <TableHead className="text-right">Rows</TableHead>
                    <TableHead className="text-right">Columns</TableHead>
                    <TableHead className="text-right">Size</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredData.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8">
                        <p className="text-muted-foreground">No files found</p>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredData.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
                              <FileSpreadsheet className="h-5 w-5 text-muted-foreground" />
                            </div>
                            <span className="font-medium">{item.fileName}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {item.rows.toLocaleString()}
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {item.columns}
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {item.processedSize || item.originalSize}
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {formatDate(item.uploadDate)}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={item.status === "processed" ? "default" : "secondary"}
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
                              <DropdownMenuItem asChild>
                                <Link href="/insights" className="flex items-center">
                                  <BarChart3 className="mr-2 h-4 w-4" />
                                  View Insights
                                </Link>
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                disabled={item.status !== "processed"}
                              >
                                <Download className="mr-2 h-4 w-4" />
                                Download
                              </DropdownMenuItem>
                              <DropdownMenuItem className="text-destructive">
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
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

export const unstable_settings = { suspense: true }
