"use client"

import { useState, useEffect } from "react"
import dynamic from "next/dynamic"

const COLORS = ['#10b981', '#ef4444', '#f59e0b']

interface PieChartData {
  name: string
  value: number
}

interface PieChartWrapperProps {
  data: PieChartData[]
  height?: number
}

export function PieChartWrapper({ data, height = 200 }: PieChartWrapperProps) {
  const [ChartComponents, setChartComponents] = useState<any>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    // Only load on client side
    if (typeof window === "undefined") return

    const loadChart = async () => {
      try {
        const recharts = await import("recharts")
        setChartComponents({
          PieChart: recharts.PieChart,
          Pie: recharts.Pie,
          Cell: recharts.Cell,
          ResponsiveContainer: recharts.ResponsiveContainer,
          Legend: recharts.Legend,
          Tooltip: recharts.Tooltip,
        })
      } catch (e) {
        console.warn("Recharts not available, charts disabled")
        setError(true)
      }
    }

    loadChart()
  }, [])

  if (error || !ChartComponents || data.length === 0) {
    // Fallback: show data as text
    return (
      <div className="flex items-center justify-center h-48 text-muted-foreground">
        <div className="text-center">
          <div className="text-sm mb-2">Chart unavailable</div>
          <div className="text-xs space-y-1">
            {data.map((item, i) => (
              <div key={i} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: COLORS[i % COLORS.length] }}
                />
                <span>
                  {item.name}: {item.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } = ChartComponents

  return (
    <div style={{ height: `${height}px` }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
