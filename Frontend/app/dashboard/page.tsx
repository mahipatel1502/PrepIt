"use client"

import Link from "next/link"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Upload,
  BarChart3,
  History,
  ArrowRight,
  FileSpreadsheet,
  Sparkles,
  Zap,
} from "lucide-react"

// Mock recent activity data
const recentActivity = [
  {
    id: 1,
    fileName: "sales_data_2024.csv",
    action: "Preprocessed",
    date: "2 hours ago",
    status: "completed",
  },
  {
    id: 2,
    fileName: "customer_segments.xlsx",
    action: "Uploaded",
    date: "5 hours ago",
    status: "pending",
  },
  {
    id: 3,
    fileName: "product_inventory.csv",
    action: "Preprocessed",
    date: "Yesterday",
    status: "completed",
  },
]

const quickActions = [
  {
    title: "Upload Dataset",
    description: "Upload CSV or Excel files for preprocessing",
    href: "/upload",
    icon: Upload,
  },
  {
    title: "View Insights",
    description: "Analyze statistics and visualizations",
    href: "/insights",
    icon: BarChart3,
  },
  {
    title: "Browse History",
    description: "Access previously processed datasets",
    href: "/history",
    icon: History,
  },
]

const features = [
  {
    icon: Sparkles,
    title: "AI-Powered Cleaning",
    description: "Automatically detect and handle missing values, outliers, and inconsistencies",
  },
  {
    icon: Zap,
    title: "Fast Processing",
    description: "Process large datasets in seconds with optimized algorithms",
  },
  {
    icon: FileSpreadsheet,
    title: "Multiple Formats",
    description: "Support for CSV, XLS, and XLSX file formats",
  },
]

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Welcome back! Start preprocessing your data for machine learning.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-3">
          {quickActions.map((action) => (
            <Card key={action.title} className="group hover:border-primary/50 transition-colors">
              <Link href={action.href}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
                      <action.icon className="h-5 w-5" />
                    </div>
                    <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-foreground transition-colors" />
                  </div>
                  <CardTitle className="text-lg mt-4">{action.title}</CardTitle>
                  <CardDescription>{action.description}</CardDescription>
                </CardHeader>
              </Link>
            </Card>
          ))}
        </div>

        {/* Features Overview */}
        <Card>
          <CardHeader>
            <CardTitle>What Prepit Can Do</CardTitle>
            <CardDescription>
              AI-powered data preprocessing for machine learning workflows
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-3">
              {features.map((feature) => (
                <div key={feature.title} className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-secondary">
                    <feature.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-medium">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Your latest dataset operations</CardDescription>
            </div>
            <Button variant="outline" size="sm" asChild>
              <Link href="/history">View All</Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-secondary/50"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-background">
                      <FileSpreadsheet className="h-5 w-5 text-muted-foreground" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">{item.fileName}</p>
                      <p className="text-xs text-muted-foreground">
                        {item.action} • {item.date}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant={item.status === "completed" ? "default" : "secondary"}
                  >
                    {item.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* CTA */}
        <Card className="bg-primary text-primary-foreground">
          <CardContent className="flex flex-col md:flex-row items-center justify-between gap-4 py-6">
            <div>
              <h3 className="text-lg font-semibold">Ready to preprocess your data?</h3>
              <p className="text-primary-foreground/80 mt-1">
                Upload your dataset and let AI handle the cleaning
              </p>
            </div>
            <Button variant="secondary" size="lg" asChild>
              <Link href="/upload">
                <Upload className="mr-2 h-4 w-4" />
                Upload Dataset
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
