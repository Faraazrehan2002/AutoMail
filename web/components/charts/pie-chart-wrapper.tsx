"use client"

import { useState, useEffect } from "react"

const COLORS = ['#10b981', '#ef4444', '#f59e0b']

interface PieChartData {
  name: string
  value: number
  color?: string
}

interface PieChartWrapperProps {
  data: PieChartData[]
  height?: number
}

export function PieChartWrapper({ data, height = 200 }: PieChartWrapperProps) {
  const [ChartComponent, setChartComponent] = useState<React.ComponentType<{ data: PieChartData[], height: number }> | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Only load on client side, after mount
    if (typeof window === "undefined") return

    const loadChart = async () => {
      try {
        // Use dynamic import to avoid build-time analysis
        const recharts = await import("recharts")
        const { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } = recharts
        
        const Chart = ({ data, height }: { data: PieChartData[], height: number }) => {
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
                      <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )
        }
        
        setChartComponent(() => Chart)
      } catch (error) {
        console.warn("Failed to load recharts:", error)
      } finally {
        setLoading(false)
      }
    }

    loadChart()
  }, [])

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-muted-foreground">
        <div className="text-center">
          <div className="text-sm mb-2">No data available</div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48 text-muted-foreground">
        <div className="text-sm">Loading chart...</div>
      </div>
    )
  }

  if (!ChartComponent) {
    // Fallback: show data as text
    return (
      <div className="flex items-center justify-center h-48 text-muted-foreground">
        <div className="text-center">
          <div className="text-sm mb-2">Chart data:</div>
          <div className="text-xs space-y-1">
            {data.map((item, i) => (
              <div key={i} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.color || COLORS[i % COLORS.length] }}
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

  return <ChartComponent data={data} height={height} />
}
