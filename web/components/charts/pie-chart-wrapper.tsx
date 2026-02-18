"use client"

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
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-muted-foreground">
        <div className="text-center">
          <div className="text-sm mb-2">No data available</div>
        </div>
      </div>
    )
  }

  // Calculate total for percentages
  const total = data.reduce((sum, item) => sum + item.value, 0)
  
  // Calculate angles for the pie chart
  let currentAngle = 0
  const segments = data.map((item, index) => {
    const percentage = (item.value / total) * 100
    const angle = (item.value / total) * 360
    const startAngle = currentAngle
    currentAngle += angle
    
    return {
      ...item,
      percentage,
      angle,
      startAngle,
      color: item.color || COLORS[index % COLORS.length],
    }
  })

  return (
    <div className="flex flex-col items-center justify-center" style={{ height: `${height}px` }}>
      {/* CSS-based pie chart */}
      <div className="relative w-48 h-48 mb-4">
        <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
          {segments.map((segment, index) => {
            const { startAngle, angle, color } = segment
            const endAngle = startAngle + angle
            
            // Calculate path for pie slice
            const startAngleRad = (startAngle * Math.PI) / 180
            const endAngleRad = (endAngle * Math.PI) / 180
            const largeArcFlag = angle > 180 ? 1 : 0
            
            const x1 = 50 + 50 * Math.cos(startAngleRad)
            const y1 = 50 + 50 * Math.sin(startAngleRad)
            const x2 = 50 + 50 * Math.cos(endAngleRad)
            const y2 = 50 + 50 * Math.sin(endAngleRad)
            
            const pathData = [
              `M 50 50`,
              `L ${x1} ${y1}`,
              `A 50 50 0 ${largeArcFlag} 1 ${x2} ${y2}`,
              `Z`,
            ].join(' ')
            
            return (
              <path
                key={index}
                d={pathData}
                fill={color}
                stroke="white"
                strokeWidth="0.5"
                className="transition-opacity hover:opacity-80"
              />
            )
          })}
        </svg>
        
        {/* Center text with total */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-lg font-bold text-foreground">{total}</div>
            <div className="text-xs text-muted-foreground">Total</div>
          </div>
        </div>
      </div>
      
      {/* Legend */}
      <div className="w-full space-y-2">
        {segments.map((segment, index) => (
          <div key={index} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: segment.color }}
              />
              <span className="text-foreground">{segment.name}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">{segment.value}</span>
              <span className="text-muted-foreground w-12 text-right">
                ({segment.percentage.toFixed(1)}%)
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
