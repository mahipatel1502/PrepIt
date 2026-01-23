"use client"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"

interface DataTablePreviewProps {
  data: Record<string, unknown>[]
  columns: string[]
  maxRows?: number
}

export function DataTablePreview({
  data,
  columns,
  maxRows = 10,
}: DataTablePreviewProps) {
  const displayData = data.slice(0, maxRows)
  const hasMore = data.length > maxRows

  const formatCellValue = (value: unknown): string => {
    if (value === null || value === undefined) return "—"
    if (typeof value === "number") return value.toLocaleString()
    if (typeof value === "boolean") return value ? "Yes" : "No"
    return String(value)
  }

  const getCellStyle = (value: unknown): string => {
    if (value === null || value === undefined) return "text-muted-foreground italic"
    if (typeof value === "number") return "font-mono tabular-nums"
    return ""
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">Data Preview</CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">{columns.length} columns</Badge>
            <Badge variant="secondary">{data.length} rows</Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="w-full">
          <div className="min-w-[800px]">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="w-12 text-center font-semibold">#</TableHead>
                  {columns.map((column) => (
                    <TableHead key={column} className="font-semibold">
                      {column}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {displayData.map((row, rowIndex) => (
                  <TableRow key={rowIndex}>
                    <TableCell className="text-center text-muted-foreground text-sm">
                      {rowIndex + 1}
                    </TableCell>
                    {columns.map((column) => (
                      <TableCell
                        key={column}
                        className={getCellStyle(row[column])}
                      >
                        {formatCellValue(row[column])}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </ScrollArea>
        {hasMore && (
          <div className="px-4 py-3 border-t border-border">
            <p className="text-sm text-muted-foreground text-center">
              Showing {maxRows} of {data.length} rows
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
