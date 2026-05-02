"use client"

import { useEffect, useMemo, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
} from "recharts"
import {
  AlertCircle,
  ArrowLeft,
  Clock3,
  Database,
  FileSpreadsheet,
  Loader2,
  Sparkles,
} from "lucide-react"
import { apiClient, type HistoryInsightsData } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

const chartColors = ["#ffffff", "#d4d4d4", "#aaaaaa", "#7f7f7f", "#5d5d5d", "#3f3f3f"]

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

function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-"
  }
  return new Intl.NumberFormat("en-US").format(value)
}

function formatMetric(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-"
  }
  if (Math.abs(value) >= 1000) return formatNumber(value)
  return Number(value).toFixed(2)
}

function formatCorrelationValue(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-"
  }
  return value.toFixed(2)
}

function getCorrelationCellStyle(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return {
      backgroundColor: "rgba(120, 120, 120, 0.12)",
      color: "var(--muted-foreground)",
    }
  }

  const abs = Math.min(1, Math.abs(value))
  const base = value >= 0 ? "34, 197, 94" : "239, 68, 68"
  const alpha = 0.18 + abs * 0.62
  const textColor = abs >= 0.55 ? "white" : "var(--foreground)"

  return {
    backgroundColor: `rgba(${base}, ${alpha.toFixed(3)})`,
    color: textColor,
  }
}

export default function SingleFileInsightsPage() {
  const params = useParams<{ historyId: string }>()
  const router = useRouter()
  const { toast } = useToast()

  const historyId = params?.historyId || ""
  const [insights, setInsights] = useState<HistoryInsightsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchInsights = async () => {
      if (!historyId) {
        setError("Missing history id")
        setIsLoading(false)
        return
      }

      setIsLoading(true)
      setError(null)

      try {
        const response = await apiClient.getHistoryInsights(historyId)
        setInsights(response.data)
      } catch (error: any) {
        console.error("Failed to load insights:", error)
        setInsights(null)
        setError(error.message || "Failed to load insights")
        toast({
          title: "Error",
          description: "Failed to load file insights",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchInsights()
  }, [historyId, toast])

  const columnTypeData = useMemo(
    () => (insights?.column_type_distribution || []).filter((item) => item.value > 0),
    [insights]
  )

  const missingData = useMemo(
    () => (insights?.missing_values_by_column || []).slice(0, 20),
    [insights]
  )

  const numericStats = useMemo(
    () => insights?.numerical_statistics || [],
    [insights]
  )

  const correlationMatrix = useMemo(() => {
    if (!insights) {
      return { columns: [] as string[], values: [] as Array<Array<number | null>> }
    }

    const matrix = insights.correlation_matrix
    if (matrix && matrix.columns?.length > 0 && matrix.values?.length > 0) {
      return matrix
    }

    // Fallback for older records where only pair list exists.
    const pairs = insights.correlation_pairs || []
    if (pairs.length === 0) {
      return { columns: [] as string[], values: [] as Array<Array<number | null>> }
    }

    const columns: string[] = []
    pairs.forEach((pair) => {
      if (!columns.includes(pair.left)) columns.push(pair.left)
      if (!columns.includes(pair.right)) columns.push(pair.right)
    })

    const size = columns.length
    const values: Array<Array<number | null>> = Array.from(
      { length: size },
      () => Array.from({ length: size }, () => null)
    )

    for (let i = 0; i < size; i++) {
      values[i][i] = 1
    }

    const indexByColumn = new Map(columns.map((name, idx) => [name, idx]))
    pairs.forEach((pair) => {
      if (pair.correlation === null || pair.correlation === undefined) return
      const i = indexByColumn.get(pair.left)
      const j = indexByColumn.get(pair.right)
      if (i === undefined || j === undefined) return
      values[i][j] = pair.correlation
      values[j][i] = pair.correlation
    })

    return { columns, values }
  }, [insights])

  const profileCoverage = useMemo(() => {
    const hasDistribution = columnTypeData.length > 0 || (insights?.column_details?.length || 0) > 0
    const hasMissing = missingData.length > 0 || (insights?.outlier_summary?.length || 0) > 0
    const hasStats = numericStats.length > 0
    const hasCorrelation = correlationMatrix.columns.length >= 2 || (insights?.correlation_pairs?.length || 0) > 0
    const tabsWithData = [hasDistribution, hasMissing, hasStats, hasCorrelation].filter(Boolean).length

    return {
      hasDistribution,
      hasMissing,
      hasStats,
      hasCorrelation,
      tabsWithData,
    }
  }, [columnTypeData, correlationMatrix.columns.length, insights, missingData.length, numericStats.length])

  const isPartialProfile = profileCoverage.tabsWithData < 4
  const isMinimalStorageProfile = insights?.profile_storage_mode === "minimal"

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <div className="text-center space-y-3">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Loading insights...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error || !insights) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <Button variant="outline" onClick={() => router.push("/insights")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Insights List
          </Button>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Unable to load insights</AlertTitle>
            <AlertDescription>{error || "Insights are not available."}</AlertDescription>
          </Alert>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <FileSpreadsheet className="h-4 w-4" />
              <span>{formatDate(insights.created_at)}</span>
              <Badge variant="outline">{insights.status}</Badge>
            </div>
            <h1 className="text-2xl font-bold tracking-tight">{insights.original_file_name}</h1>
            {insights.processed_file_name && (
              <p className="text-sm text-muted-foreground">{insights.processed_file_name}</p>
            )}
          </div>
          <Button variant="outline" onClick={() => router.push("/insights")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to List
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-5">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">Rows</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(insights.summary.original_rows)}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {formatNumber(insights.summary.rows_removed)} removed in preprocessing
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">Columns</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(insights.summary.original_columns)}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {formatNumber(insights.summary.columns_added)} engineered
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">Completeness</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {insights.dataset_overview?.completeness_pct ?? insights.summary.data_quality_score}%
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {formatNumber(insights.dataset_overview?.missing_cells ?? 0)} missing cells
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">Duplicates</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(insights.dataset_overview?.duplicate_rows ?? 0)}</div>
              <p className="text-xs text-muted-foreground mt-1">Detected before cleaning</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">Runtime</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{insights.summary.processing_time_seconds}s</div>
              <p className="text-xs text-muted-foreground mt-1">Preprocessing duration</p>
            </CardContent>
          </Card>
        </div>

        {isPartialProfile && (
          <Alert>
            <Sparkles className="h-4 w-4" />
            <AlertTitle>{isMinimalStorageProfile ? "Compact Insights Mode" : "Partial Insights Data"}</AlertTitle>
            <AlertDescription>
              {isMinimalStorageProfile
                ? "This profile was compacted to fit backend storage limits, so some sections may be reduced. Reprocess the file for a fully expanded profile."
                : "Some advanced sections are not available for this record. Reprocessing this file will regenerate the full profile."}
            </AlertDescription>
          </Alert>
        )}

        <Tabs defaultValue="distribution" className="space-y-4">
          <TabsList>
            <TabsTrigger value="distribution">Distribution</TabsTrigger>
            <TabsTrigger value="missing">Missing Values</TabsTrigger>
            <TabsTrigger value="statistics">Statistics</TabsTrigger>
            <TabsTrigger value="correlation">Correlation</TabsTrigger>
          </TabsList>

          <TabsContent value="distribution" className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Data Types Distribution</CardTitle>
                  <CardDescription>Breakdown of inferred column types</CardDescription>
                </CardHeader>
                <CardContent>
                  {columnTypeData.length > 0 ? (
                    <ChartContainer config={{ value: { label: "Columns" } }} className="h-[320px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={columnTypeData}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            innerRadius={68}
                            outerRadius={110}
                            paddingAngle={4}
                            label={({ name, value }) => `${name}: ${value}`}
                          >
                            {columnTypeData.map((entry, index) => (
                              <Cell key={`${entry.name}-${index}`} fill={chartColors[index % chartColors.length]} />
                            ))}
                          </Pie>
                          <ChartTooltip content={<ChartTooltipContent />} />
                        </PieChart>
                      </ResponsiveContainer>
                    </ChartContainer>
                  ) : (
                    <p className="text-sm text-muted-foreground py-8 text-center">No distribution data available.</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Column Details</CardTitle>
                  <CardDescription>Type, missing values, and uniqueness per column</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-[420px] overflow-auto pr-1">
                    {(insights.column_details || []).map((col) => (
                      <div
                        key={col.column}
                        className="flex items-center justify-between p-3 rounded-lg bg-secondary/50"
                      >
                        <div className="flex items-center gap-3">
                          <code className="text-sm font-mono font-medium">{col.column}</code>
                          <Badge variant="outline" className="text-xs">
                            {col.type}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>{col.missing_count} nulls</span>
                          <span>{col.unique_count} unique</span>
                        </div>
                      </div>
                    ))}
                    {(insights.column_details || []).length === 0 && (
                      <p className="text-sm text-muted-foreground">No column-level profile available.</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="missing" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Missing Values by Column</CardTitle>
                <CardDescription>Columns with highest null counts in source file</CardDescription>
              </CardHeader>
              <CardContent>
                {missingData.length > 0 ? (
                  <ChartContainer config={{ missing_count: { label: "Missing", color: "#ffffff" } }} className="h-[420px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={missingData}
                        layout="vertical"
                        margin={{ top: 5, right: 20, left: 70, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                        <XAxis type="number" />
                        <YAxis dataKey="column" type="category" width={130} />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Bar dataKey="missing_count" fill="#ffffff" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                ) : (
                  <p className="text-sm text-muted-foreground py-8 text-center">No missing values detected.</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Outlier Summary</CardTitle>
                <CardDescription>IQR-based outlier percentages by numeric column</CardDescription>
              </CardHeader>
              <CardContent>
                {(insights.outlier_summary || []).length > 0 ? (
                  <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                    {(insights.outlier_summary || []).map((item) => (
                      <div key={item.column} className="rounded-lg border p-3">
                        <p className="font-mono text-sm">{item.column}</p>
                        <p className="text-2xl font-semibold mt-2">{item.outlier_pct}%</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {item.outlier_count} potential outliers
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No outlier summary available.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="statistics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Numerical Column Statistics</CardTitle>
                <CardDescription>Descriptive statistics for numeric features</CardDescription>
              </CardHeader>
              <CardContent>
                {numericStats.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border">
                          <th className="text-left py-3 px-4 font-semibold">Column</th>
                          <th className="text-right py-3 px-4 font-semibold">Mean</th>
                          <th className="text-right py-3 px-4 font-semibold">Median</th>
                          <th className="text-right py-3 px-4 font-semibold">Std Dev</th>
                          <th className="text-right py-3 px-4 font-semibold">Min</th>
                          <th className="text-right py-3 px-4 font-semibold">Max</th>
                        </tr>
                      </thead>
                      <tbody>
                        {numericStats.map((stat) => (
                          <tr key={stat.column} className="border-b border-border/50">
                            <td className="py-3 px-4 font-mono">{stat.column}</td>
                            <td className="text-right py-3 px-4 tabular-nums">{formatMetric(stat.mean)}</td>
                            <td className="text-right py-3 px-4 tabular-nums">{formatMetric(stat.median)}</td>
                            <td className="text-right py-3 px-4 tabular-nums">{formatMetric(stat.std)}</td>
                            <td className="text-right py-3 px-4 tabular-nums">{formatMetric(stat.min)}</td>
                            <td className="text-right py-3 px-4 tabular-nums">{formatMetric(stat.max)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No numerical statistics available.</p>
                )}
              </CardContent>
            </Card>

            <div className="grid gap-4 lg:grid-cols-3">
              {numericStats.slice(0, 6).map((stat) => (
                <Card key={stat.column}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base font-mono">{stat.column}</CardTitle>
                    <CardDescription>Distribution summary</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Range</span>
                        <span className="font-medium">
                          {formatMetric(stat.min)} - {formatMetric(stat.max)}
                        </span>
                      </div>
                      <div className="h-2 bg-secondary rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary"
                          style={{
                            width: `${Math.min(100, Math.max(
                              0,
                              stat.min !== null &&
                              stat.max !== null &&
                              stat.mean !== null &&
                              stat.max !== stat.min
                                ? ((stat.mean - stat.min) / (stat.max - stat.min)) * 100
                                : 0
                            ))}%`,
                          }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Q1: {formatMetric(stat.q1)}</span>
                        <span>Median: {formatMetric(stat.median)}</span>
                        <span>Q3: {formatMetric(stat.q3)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="correlation" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Correlation Matrix</CardTitle>
                <CardDescription>
                  Square heatmap view with Pearson correlation values in each cell
                </CardDescription>
              </CardHeader>
              <CardContent>
                {correlationMatrix.columns.length >= 2 ? (
                  <div className="space-y-3">
                    <div className="overflow-auto rounded-lg border border-border/60 p-2">
                      <table className="border-separate border-spacing-1">
                        <thead>
                          <tr>
                            <th className="h-16 w-24 min-w-24" />
                            {correlationMatrix.columns.map((column) => (
                              <th
                                key={`header-${column}`}
                                className="h-16 w-16 min-w-16 px-1 text-[10px] font-medium text-muted-foreground"
                                title={column}
                              >
                                <div className="line-clamp-2 break-all">{column}</div>
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {correlationMatrix.columns.map((rowColumn, rowIndex) => (
                            <tr key={`row-${rowColumn}`}>
                              <th
                                className="w-24 min-w-24 px-2 py-1 text-left text-[10px] font-medium text-muted-foreground"
                                title={rowColumn}
                              >
                                <div className="line-clamp-2 break-all">{rowColumn}</div>
                              </th>
                              {correlationMatrix.columns.map((colColumn, colIndex) => {
                                const value = correlationMatrix.values[rowIndex]?.[colIndex] ?? null
                                return (
                                  <td
                                    key={`cell-${rowColumn}-${colColumn}`}
                                    className="h-16 w-16 min-w-16 rounded-md text-center text-xs font-mono font-semibold"
                                    style={getCorrelationCellStyle(value)}
                                    title={`${rowColumn} vs ${colColumn}: ${formatCorrelationValue(value)}`}
                                  >
                                    {formatCorrelationValue(value)}
                                  </td>
                                )
                              })}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span>-1.0</span>
                      <div className="h-2 w-48 rounded-full bg-gradient-to-r from-red-500/70 via-gray-400/50 to-green-500/70" />
                      <span>+1.0</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground py-8 text-center">
                    Not enough numeric columns for correlation analysis.
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Insight Highlights</CardTitle>
                <CardDescription>Auto-generated findings from dataset profile</CardDescription>
              </CardHeader>
              <CardContent>
                {(insights.highlights || []).length > 0 ? (
                  <div className="space-y-3">
                    {(insights.highlights || []).map((item, index) => (
                      <div key={`${item}-${index}`} className="rounded-lg bg-secondary/50 p-3 text-sm">
                        {item}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No highlights available.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <Card>
          <CardHeader>
            <CardTitle>Preprocessing Impact</CardTitle>
            <CardDescription>Changes applied by preprocessing pipeline</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <Database className="h-4 w-4" />
                Columns dropped
              </p>
              <p className="text-2xl font-semibold mt-2">{insights.summary.columns_dropped}</p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                Features engineered
              </p>
              <p className="text-2xl font-semibold mt-2">{insights.summary.features_engineered}</p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <Clock3 className="h-4 w-4" />
                Processing time
              </p>
              <p className="text-2xl font-semibold mt-2">{insights.summary.processing_time_seconds}s</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
