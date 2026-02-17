"use client"

import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { motion } from "framer-motion"
import { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface StatsCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  description?: string
  trend?: {
    value: string
    isPositive: boolean
  }
}

export function StatsCard({ title, value, icon: Icon, description, trend }: StatsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <Card className="relative overflow-hidden border-primary/20 hover:border-primary/40 transition-all duration-300 group">
        {/* Animated gradient border */}
        <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-purple-500/20 to-primary/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-xl" />
        <div className="relative bg-card/80 backdrop-blur-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {title}
            </CardTitle>
            <motion.div
              whileHover={{ rotate: 360, scale: 1.1 }}
              transition={{ duration: 0.5 }}
            >
              <Icon className="h-4 w-4 text-primary" />
            </motion.div>
          </CardHeader>
          <CardContent>
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1 }}
              className="text-2xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent"
            >
              {value}
            </motion.div>
            {description && (
              <p className="text-xs text-muted-foreground mt-1">{description}</p>
            )}
            {trend && (
              <p
                className={cn(
                  "text-xs mt-1",
                  trend.isPositive ? "text-green-600" : "text-red-600"
                )}
              >
                {trend.value}
              </p>
            )}
          </CardContent>
        </div>
      </Card>
    </motion.div>
  )
}
