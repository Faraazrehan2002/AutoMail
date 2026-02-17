'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowLeft, RefreshCw, CheckCircle2, XCircle, Clock } from 'lucide-react'
import { getBatchStatus, type BatchStatus } from '@/src/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { PieChartWrapper } from '@/components/charts/pie-chart-wrapper'

export default function BatchDetailPage() {
  const router = useRouter()
  const params = useParams()
  const jobId = params.jobId as string
  const batchId = params.batchId as string

  const [batch, setBatch] = useState<BatchStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadBatch()
  }, [jobId, batchId])

  async function loadBatch() {
    try {
      setLoading(true)
      const data = await getBatchStatus(jobId, batchId)
      setBatch(data)
    } catch (error: any) {
      console.error('Failed to load batch:', error)
      router.push(`/jobs/${jobId}`)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64" />
        <Skeleton className="h-96" />
      </div>
    )
  }

  if (!batch) {
    return null
  }

  const chartData = [
    { name: 'Sent', value: batch.sent },
    { name: 'Failed', value: batch.failed },
    { name: 'Queued', value: batch.queued },
  ]

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Button
          variant="ghost"
          onClick={() => router.push(`/jobs/${jobId}`)}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Job
        </Button>
        <h1 className="text-3xl font-bold">Batch Results</h1>
        <p className="text-muted-foreground mt-2">
          Batch ID: {batch.batch_id} • Created {new Date(batch.created_at).toLocaleString()}
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Batch Statistics</CardTitle>
                <CardDescription>
                  Overview of email sending results
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={loadBatch}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <div className="text-2xl font-bold">{batch.total_recipients}</div>
                <div className="text-sm text-muted-foreground">Total</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-green-500/10">
                <div className="text-2xl font-bold text-green-600">{batch.sent}</div>
                <div className="text-sm text-muted-foreground">Sent</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-red-500/10">
                <div className="text-2xl font-bold text-red-600">{batch.failed}</div>
                <div className="text-sm text-muted-foreground">Failed</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-yellow-500/10">
                <div className="text-2xl font-bold text-yellow-600">{batch.queued}</div>
                <div className="text-sm text-muted-foreground">Queued</div>
              </div>
            </div>

            {chartData.some(d => d.value > 0) && (
              <PieChartWrapper data={chartData} height={256} />
            )}

            <div>
              <h3 className="text-lg font-semibold mb-4">Recipient Status</h3>
              <div className="border rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-border">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Email</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Message ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Error</th>
                      </tr>
                    </thead>
                    <tbody className="bg-background divide-y divide-border">
                      {batch.results.map((result, index) => (
                        <motion.tr
                          key={result.email}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.02 }}
                          className="hover:bg-muted/50 transition-colors"
                        >
                          <td className="px-6 py-4 whitespace-nowrap text-sm">{result.email}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <Badge
                              variant={
                                result.status === 'sent'
                                  ? 'success'
                                  : result.status === 'failed'
                                  ? 'destructive'
                                  : 'secondary'
                              }
                              className="gap-1"
                            >
                              {result.status === 'sent' && <CheckCircle2 className="h-3 w-3" />}
                              {result.status === 'failed' && <XCircle className="h-3 w-3" />}
                              {result.status === 'queued' && <Clock className="h-3 w-3" />}
                              {result.status}
                            </Badge>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                            {result.sendgrid_message_id || '-'}
                          </td>
                          <td className="px-6 py-4 text-sm text-destructive">
                            {result.error_message || '-'}
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
