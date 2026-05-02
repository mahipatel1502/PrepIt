"use client"

import { useEffect, useMemo, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import {
  AlertCircle,
  ArrowLeft,
  BrainCircuit,
  CheckCircle2,
  Download,
  Loader2,
  Sparkles,
} from "lucide-react"
import {
  apiClient,
  type AutoMLColumnProfile,
  type AutoMLLeaderboardEntry,
  type AutoMLSchemaData,
  type AutoMLTrainData,
} from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "-"
  return new Intl.NumberFormat("en-US").format(value)
}

function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "-"
  return value.toFixed(4)
}

function metricSummary(entry: AutoMLLeaderboardEntry, problemType: string): string {
  if (!entry.metrics || Object.keys(entry.metrics).length === 0) return "-"
  const keys =
    problemType === "classification"
      ? ["f1_weighted", "accuracy", "precision_weighted", "recall_weighted", "roc_auc_ovr"]
      : ["r2", "mae", "rmse"]

  const parts: string[] = []
  keys.forEach((key) => {
    const value = entry.metrics[key]
    if (value !== null && value !== undefined && !Number.isNaN(value)) {
      parts.push(`${key}: ${Number(value).toFixed(3)}`)
    }
  })
  return parts.length > 0 ? parts.join(" • ") : "-"
}

export default function AutoMLDetailPage() {
  const params = useParams<{ historyId: string }>()
  const router = useRouter()
  const { toast } = useToast()

  const historyId = params?.historyId || ""
  const [schema, setSchema] = useState<AutoMLSchemaData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isTraining, setIsTraining] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [selectedTarget, setSelectedTarget] = useState("")
  const [testSize, setTestSize] = useState("0.2")
  const [randomState, setRandomState] = useState("42")
  const [trainResult, setTrainResult] = useState<AutoMLTrainData | null>(null)

  useEffect(() => {
    const fetchSchema = async () => {
      if (!historyId) {
        setError("Missing history id")
        setIsLoading(false)
        return
      }

      setIsLoading(true)
      setError(null)
      try {
        const response = await apiClient.getAutoMLSchema(historyId)
        setSchema(response.data)
        const firstTarget = response.data.target_candidates[0] || ""
        setSelectedTarget(firstTarget)
      } catch (err: any) {
        console.error("Failed to load AutoML schema:", err)
        setError(err.message || "Failed to load dataset schema")
        toast({
          title: "Error",
          description: "Could not load dataset schema for AutoML",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchSchema()
  }, [historyId, toast])

  const topColumns = useMemo(() => {
    if (!schema) return []
    return schema.column_profiles.slice(0, 25)
  }, [schema])

  const handleTrain = async () => {
    if (!schema || !selectedTarget) {
      setError("Please select a target column")
      return
    }

    const parsedRandomState = Number.parseInt(randomState, 10)
    if (Number.isNaN(parsedRandomState) || parsedRandomState < 0) {
      setError("Random state must be a valid non-negative integer")
      return
    }

    setIsTraining(true)
    setError(null)
    try {
      const response = await apiClient.trainAutoML({
        history_id: schema.history_id,
        target_column: selectedTarget,
        test_size: Number(testSize),
        random_state: parsedRandomState,
      })
      setTrainResult(response.data)
      toast({
        title: "AutoML completed",
        description: `Best model selected: ${response.data.best_model.model_name}`,
      })
    } catch (err: any) {
      console.error("AutoML training failed:", err)
      setTrainResult(null)
      setError(err.message || "AutoML training failed")
      toast({
        title: "Training failed",
        description: err.message || "AutoML training failed",
        variant: "destructive",
      })
    } finally {
      setIsTraining(false)
    }
  }

  const handleDownloadModel = async () => {
    if (!trainResult) return
    try {
      await apiClient.downloadAutoMLModel(
        trainResult.run_id,
        `automl_${trainResult.best_model.model_key}_${trainResult.run_id}.joblib`
      )
      toast({
        title: "Download started",
        description: "Best model artifact download started",
      })
    } catch (err: any) {
      console.error("Download failed:", err)
      toast({
        title: "Download failed",
        description: err.message || "Could not download model artifact",
        variant: "destructive",
      })
    }
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <div className="text-center space-y-3">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Loading dataset schema...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error && !schema) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <Button variant="outline" onClick={() => router.push("/automl")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to AutoML List
          </Button>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Unable to load AutoML page</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
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
            <h1 className="text-2xl font-bold tracking-tight">AutoML Training</h1>
            <p className="text-muted-foreground">
              {schema?.original_file_name || "Selected file"}
            </p>
            {schema?.processed_file_name && (
              <p className="text-xs text-muted-foreground">{schema.processed_file_name}</p>
            )}
          </div>
          <Button variant="outline" onClick={() => router.push("/automl")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to List
          </Button>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Training Setup</CardTitle>
            <CardDescription>Select target and run AutoML on processed dataset</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">Rows</p>
                <p className="text-2xl font-semibold mt-2">{formatNumber(schema?.rows)}</p>
              </div>
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">Columns</p>
                <p className="text-2xl font-semibold mt-2">{formatNumber(schema?.columns)}</p>
              </div>
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">Target candidates</p>
                <p className="text-2xl font-semibold mt-2">{formatNumber(schema?.target_candidates.length)}</p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <p className="text-sm font-medium">Target column</p>
                <Select value={selectedTarget} onValueChange={setSelectedTarget}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select target column" />
                  </SelectTrigger>
                  <SelectContent>
                    {(schema?.target_candidates || []).map((column) => (
                      <SelectItem key={column} value={column}>
                        {column}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium">Test size</p>
                <Select value={testSize} onValueChange={setTestSize}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0.2">20%</SelectItem>
                    <SelectItem value="0.25">25%</SelectItem>
                    <SelectItem value="0.3">30%</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium">Random state</p>
                <Input value={randomState} onChange={(e) => setRandomState(e.target.value)} />
              </div>
            </div>

            <Button onClick={handleTrain} disabled={isTraining || !selectedTarget}>
              {isTraining ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Training models...
                </>
              ) : (
                <>
                  <BrainCircuit className="mr-2 h-4 w-4" />
                  Run AutoML
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Column Snapshot</CardTitle>
            <CardDescription>First 25 columns from processed dataset</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Column</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Missing</TableHead>
                    <TableHead>Unique</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {topColumns.map((column: AutoMLColumnProfile) => (
                    <TableRow key={column.name}>
                      <TableCell className="font-mono">{column.name}</TableCell>
                      <TableCell>{column.dtype}</TableCell>
                      <TableCell>
                        {column.missing_count} ({column.missing_pct}%)
                      </TableCell>
                      <TableCell>{column.unique_count}</TableCell>
                    </TableRow>
                  ))}
                  {topColumns.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-6 text-muted-foreground">
                        No schema details available.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {trainResult && (
          <>
            <Card className="border-primary/40">
              <CardHeader>
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                      Best Model: {trainResult.best_model.model_name}
                    </CardTitle>
                    <CardDescription>
                      Auto-selected {trainResult.problem_type} model with score {formatScore(trainResult.best_model.score)}
                    </CardDescription>
                  </div>
                  <Button onClick={handleDownloadModel}>
                    <Download className="mr-2 h-4 w-4" />
                    Download Model
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-4">
                <div className="rounded-lg border p-3">
                  <p className="text-xs text-muted-foreground">Problem type</p>
                  <p className="font-semibold mt-1 capitalize">{trainResult.problem_type}</p>
                </div>
                <div className="rounded-lg border p-3">
                  <p className="text-xs text-muted-foreground">Train rows</p>
                  <p className="font-semibold mt-1">{formatNumber(trainResult.train_rows)}</p>
                </div>
                <div className="rounded-lg border p-3">
                  <p className="text-xs text-muted-foreground">Test rows</p>
                  <p className="font-semibold mt-1">{formatNumber(trainResult.test_rows)}</p>
                </div>
                <div className="rounded-lg border p-3">
                  <p className="text-xs text-muted-foreground">Feature count</p>
                  <p className="font-semibold mt-1">{formatNumber(trainResult.feature_count)}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Model Leaderboard</CardTitle>
                <CardDescription>All attempted models ranked by best score</CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Rank</TableHead>
                        <TableHead>Model</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Score</TableHead>
                        <TableHead>Fit Time</TableHead>
                        <TableHead>Metrics</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {trainResult.leaderboard.map((entry) => (
                        <TableRow key={entry.model_key}>
                          <TableCell>{entry.rank ?? "-"}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <span>{entry.model_name}</span>
                              {entry.is_best && (
                                <Badge variant="default" className="gap-1">
                                  <Sparkles className="h-3 w-3" />
                                  Best
                                </Badge>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant={entry.status === "success" ? "default" : "destructive"}>
                              {entry.status}
                            </Badge>
                          </TableCell>
                          <TableCell>{formatScore(entry.score)}</TableCell>
                          <TableCell>{entry.fit_time_seconds ? `${entry.fit_time_seconds}s` : "-"}</TableCell>
                          <TableCell className="max-w-[460px]">
                            <p className="text-xs text-muted-foreground line-clamp-2">
                              {metricSummary(entry, trainResult.problem_type)}
                            </p>
                            {entry.error && (
                              <p className="text-xs text-destructive mt-1 line-clamp-2">{entry.error}</p>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </DashboardLayout>
  )
}
