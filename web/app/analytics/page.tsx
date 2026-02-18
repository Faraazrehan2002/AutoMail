'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, Mail, CheckCircle2, XCircle, Calendar } from 'lucide-react'
import { getAnalyticsOverview, type AnalyticsOverview } from '@/src/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/hooks/use-toast'
import { StatsCard } from '@/components/stats-card'
import { PieChartWrapper } from '@/components/charts/pie-chart-wrapper'

export default function AnalyticsPage() {
  const { toast } = useToast()
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  useEffect(() => {
    loadAnalytics()
  }, [days])

  async function loadAnalytics() {
    try {
      setLoading(true)
      const data = await getAnalyticsOverview(days)
      setAnalytics(data)
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to load analytics',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const chartData = analytics ? [
    { name: 'Sent', value: analytics.total_emails_sent },
    { name: 'Failed', value: analytics.total_emails_failed },
  ] : []

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
            Analytics
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground mt-2">
            Track your email sending performance
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          {[7, 30, 90].map((d) => (
            <Button
              key={d}
              variant={days === d ? 'default' : 'outline'}
              size="sm"
              onClick={() => setDays(d)}
            >
              {d} days
            </Button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : analytics ? (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatsCard
              title="Total Jobs"
              value={analytics.total_jobs}
              icon={Calendar}
              trend={null}
            />
            <StatsCard
              title="Total Batches"
              value={analytics.total_batches}
              icon={Mail}
              trend={null}
            />
            <StatsCard
              title="Emails Sent"
              value={analytics.total_emails_sent}
              icon={CheckCircle2}
              trend={null}
            />
            <StatsCard
              title="Success Rate"
              value={`${analytics.overall_success_rate.toFixed(1)}%`}
              icon={TrendingUp}
              trend={null}
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Email Status</CardTitle>
                <CardDescription>Distribution of sent vs failed emails</CardDescription>
              </CardHeader>
              <CardContent>
                <PieChartWrapper data={chartData} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Daily Metrics</CardTitle>
                <CardDescription>Email activity over the last {days} days</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {analytics.daily_metrics.length === 0 ? (
                    <p className="text-center text-muted-foreground py-8">
                      No data available for this period
                    </p>
                  ) : (
                    analytics.daily_metrics.map((day) => (
                      <motion.div
                        key={day.date}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center justify-between p-3 rounded-lg border bg-card"
                      >
                        <div>
                          <p className="font-medium">{new Date(day.date).toLocaleDateString()}</p>
                          <p className="text-sm text-muted-foreground">
                            {day.jobs_created} jobs • {day.batches_sent} batches
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">
                            {day.emails_sent} sent / {day.emails_failed} failed
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {day.success_rate.toFixed(1)}% success
                          </p>
                        </div>
                      </motion.div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      ) : null}
    </div>
  )
}
