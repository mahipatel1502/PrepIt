"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
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
  LineChart,
  Line,
  ResponsiveContainer,
} from "recharts"

// Mock data for visualizations
const columnDistribution = [
  { column: "age", type: "numeric", nulls: 12, unique: 45 },
  { column: "salary", type: "numeric", nulls: 8, unique: 89 },
  { column: "name", type: "string", nulls: 0, unique: 100 },
  { column: "email", type: "string", nulls: 15, unique: 98 },
  { column: "department", type: "categorical", nulls: 0, unique: 5 },
  { column: "id", type: "numeric", nulls: 0, unique: 100 },
]

const dataTypeDistribution = [
  { name: "Numeric", value: 3, fill: "#ffffff" },
  { name: "String", value: 2, fill: "#a3a3a3" },
  { name: "Categorical", value: 1, fill: "#525252" },
]

const missingValuesByColumn = [
  { column: "email", missing: 15 },
  { column: "age", missing: 12 },
  { column: "salary", missing: 8 },
  { column: "name", missing: 0 },
  { column: "department", missing: 0 },
  { column: "id", missing: 0 },
]

const numericalStats = [
  { column: "age", mean: 33.2, median: 31, std: 6.8, min: 26, max: 45 },
  { column: "salary", mean: 78500, median: 76500, std: 9200, min: 65000, max: 95000 },
  { column: "id", mean: 6.5, median: 6.5, std: 3.45, min: 1, max: 12 },
]

const correlationData = [
  { pair: "age-salary", correlation: 0.72 },
  { pair: "id-age", correlation: 0.15 },
  { pair: "id-salary", correlation: 0.23 },
]

// Compute colors for dark mode (using foreground/muted colors)
const chartColors = {
  primary: "#ffffff",
  secondary: "#a3a3a3",
  tertiary: "#525252",
  accent: "#d4d4d4",
}

export default function InsightsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Data Insights</h1>
          <p className="text-muted-foreground mt-1">
            Explore statistics and visualizations for your dataset
          </p>
        </div>

        {/* Overview Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Columns
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">6</div>
              <p className="text-xs text-muted-foreground mt-1">Features analyzed</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Numeric Columns
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-muted-foreground mt-1">age, salary, id</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Categorical Columns
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1</div>
              <p className="text-xs text-muted-foreground mt-1">department</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Data Quality
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">94.2%</div>
              <p className="text-xs text-muted-foreground mt-1">Non-null values</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs for different insights */}
        <Tabs defaultValue="distribution" className="space-y-4">
          <TabsList>
            <TabsTrigger value="distribution">Distribution</TabsTrigger>
            <TabsTrigger value="missing">Missing Values</TabsTrigger>
            <TabsTrigger value="statistics">Statistics</TabsTrigger>
            <TabsTrigger value="correlation">Correlation</TabsTrigger>
          </TabsList>

          {/* Column Distribution Tab */}
          <TabsContent value="distribution" className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Data Types Distribution</CardTitle>
                  <CardDescription>
                    Breakdown of column types in your dataset
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ChartContainer
                    config={{
                      value: { label: "Columns" },
                    }}
                    className="h-[300px]"
                  >
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={dataTypeDistribution}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={5}
                          dataKey="value"
                          label={({ name, value }) => `${name}: ${value}`}
                        >
                          {dataTypeDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Pie>
                        <ChartTooltip content={<ChartTooltipContent />} />
                      </PieChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Column Details</CardTitle>
                  <CardDescription>
                    Type, null count, and unique values per column
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {columnDistribution.map((col) => (
                      <div
                        key={col.column}
                        className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <code className="text-sm font-mono font-medium">
                            {col.column}
                          </code>
                          <Badge variant="outline" className="text-xs">
                            {col.type}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>{col.nulls} nulls</span>
                          <span>{col.unique} unique</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Missing Values Tab */}
          <TabsContent value="missing" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Missing Values by Column</CardTitle>
                <CardDescription>
                  Visual representation of null/empty values in each column
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer
                  config={{
                    missing: { label: "Missing", color: chartColors.primary },
                  }}
                  className="h-[400px]"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={missingValuesByColumn}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                      <XAxis type="number" />
                      <YAxis dataKey="column" type="category" width={70} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar
                        dataKey="missing"
                        fill={chartColors.primary}
                        radius={[0, 4, 4, 0]}
                        name="Missing Values"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Missing Value Heatmap</CardTitle>
                <CardDescription>
                  Visual indicator of data completeness
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-6 gap-2">
                  {columnDistribution.map((col) => {
                    const completeness = 100 - col.nulls
                    return (
                      <div key={col.column} className="space-y-2">
                        <div
                          className="aspect-square rounded-lg flex items-center justify-center text-xs font-medium"
                          style={{
                            backgroundColor:
                              completeness === 100
                                ? "var(--success)"
                                : completeness > 90
                                  ? "var(--warning)"
                                  : "var(--destructive)",
                            color: "var(--background)",
                          }}
                        >
                          {completeness}%
                        </div>
                        <p className="text-xs text-center text-muted-foreground truncate">
                          {col.column}
                        </p>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Statistics Tab */}
          <TabsContent value="statistics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Numerical Column Statistics</CardTitle>
                <CardDescription>
                  Descriptive statistics for numeric features
                </CardDescription>
              </CardHeader>
              <CardContent>
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
                      {numericalStats.map((stat) => (
                        <tr key={stat.column} className="border-b border-border/50">
                          <td className="py-3 px-4 font-mono">{stat.column}</td>
                          <td className="text-right py-3 px-4 tabular-nums">
                            {stat.mean.toLocaleString()}
                          </td>
                          <td className="text-right py-3 px-4 tabular-nums">
                            {stat.median.toLocaleString()}
                          </td>
                          <td className="text-right py-3 px-4 tabular-nums">
                            {stat.std.toLocaleString()}
                          </td>
                          <td className="text-right py-3 px-4 tabular-nums">
                            {stat.min.toLocaleString()}
                          </td>
                          <td className="text-right py-3 px-4 tabular-nums">
                            {stat.max.toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            <div className="grid gap-4 lg:grid-cols-3">
              {numericalStats.map((stat) => (
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
                          {stat.min.toLocaleString()} - {stat.max.toLocaleString()}
                        </span>
                      </div>
                      <div className="h-2 bg-secondary rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary"
                          style={{
                            width: `${((stat.mean - stat.min) / (stat.max - stat.min)) * 100}%`,
                          }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Min: {stat.min}</span>
                        <span>Mean: {stat.mean}</span>
                        <span>Max: {stat.max}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Correlation Tab */}
          <TabsContent value="correlation" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Feature Correlation</CardTitle>
                <CardDescription>
                  Correlation coefficients between numeric columns
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer
                  config={{
                    correlation: { label: "Correlation", color: chartColors.primary },
                  }}
                  className="h-[300px]"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={correlationData}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="pair" />
                      <YAxis domain={[-1, 1]} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar
                        dataKey="correlation"
                        fill={chartColors.primary}
                        radius={[4, 4, 0, 0]}
                        name="Correlation"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Correlation Insights</CardTitle>
                <CardDescription>Key findings from correlation analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-secondary/50 rounded-lg">
                    <h4 className="font-medium mb-2">Strong Positive Correlation</h4>
                    <p className="text-sm text-muted-foreground">
                      <code className="font-mono">age</code> and{" "}
                      <code className="font-mono">salary</code> show a strong positive
                      correlation (0.72), suggesting that salary tends to increase with
                      age in this dataset.
                    </p>
                  </div>
                  <div className="p-4 bg-secondary/50 rounded-lg">
                    <h4 className="font-medium mb-2">Weak Correlations</h4>
                    <p className="text-sm text-muted-foreground">
                      <code className="font-mono">id</code> shows minimal correlation
                      with other features, which is expected as it is an identifier
                      column.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
