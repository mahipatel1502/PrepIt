"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Rows3, Columns3, AlertTriangle, Copy } from "lucide-react"

interface DatasetStats {
  rowCount: number
  columnCount: number
  missingValues: number
  duplicateRows: number
}

interface StatsCardsProps {
  stats: DatasetStats
}

export function StatsCards({ stats }: StatsCardsProps) {
  const cards = [
    {
      title: "Total Rows",
      value: stats.rowCount.toLocaleString(),
      icon: Rows3,
      description: "Records in dataset",
    },
    {
      title: "Total Columns",
      value: stats.columnCount.toLocaleString(),
      icon: Columns3,
      description: "Features detected",
    },
    {
      title: "Missing Values",
      value: stats.missingValues.toLocaleString(),
      icon: AlertTriangle,
      description: "Cells with null/empty",
      highlight: stats.missingValues > 0,
    },
    {
      title: "Duplicate Rows",
      value: stats.duplicateRows.toLocaleString(),
      icon: Copy,
      description: "Identical records",
      highlight: stats.duplicateRows > 0,
    },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {card.title}
            </CardTitle>
            <card.icon className={`h-4 w-4 ${card.highlight ? "text-warning" : "text-muted-foreground"}`} />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${card.highlight ? "text-warning" : ""}`}>
              {card.value}
            </div>
            <p className="text-xs text-muted-foreground mt-1">{card.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
