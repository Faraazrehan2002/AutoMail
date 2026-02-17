'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { Search, Filter, CheckCircle2, XCircle, Clock, ArrowLeft, RefreshCw, Loader2 } from 'lucide-react'
import { getJob, sendEmails, getBatchStatus, type JobDetail, type SendResponse, type BatchStatus } from '@/src/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/hooks/use-toast'
import { PieChartWrapper } from '@/components/charts/pie-chart-wrapper'

export default function JobDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { toast } = useToast()
  const jobId = params.jobId as string

  const [job, setJob] = useState<JobDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedRecipients, setSelectedRecipients] = useState<Set<string>>(new Set())
  const [searchQuery, setSearchQuery] = useState('')
  const [domainFilter, setDomainFilter] = useState<string>('')
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [dryRun, setDryRun] = useState(false)
  const [sending, setSending] = useState(false)
  const [sendResult, setSendResult] = useState<SendResponse | null>(null)
  const [batchStatus, setBatchStatus] = useState<BatchStatus | null>(null)

  useEffect(() => {
    loadJob()
  }, [jobId])

  useEffect(() => {
    if (sendResult?.batch_id) {
      loadBatchStatus()
    }
  }, [sendResult?.batch_id])

  async function loadJob() {
    try {
      setLoading(true)
      const data = await getJob(jobId)
      setJob(data)
    } catch (error: any) {
      console.error('Failed to load job:', error)
      toast({
        title: "Error",
        description: error.message || "Failed to load job",
        variant: "destructive",
      })
      router.push('/')
    } finally {
      setLoading(false)
    }
  }

  async function loadBatchStatus() {
    if (!sendResult?.batch_id) return
    try {
      const status = await getBatchStatus(jobId, sendResult.batch_id)
      setBatchStatus(status)
    } catch (error: any) {
      console.error('Failed to load batch status:', error)
    }
  }

  // Get unique domains
  const domains = useMemo(() => {
    if (!job) return []
    const domainSet = new Set<string>()
    job.recipients.forEach((r) => {
      const domain = r.email.split('@')[1]
      if (domain) domainSet.add(domain)
    })
    return Array.from(domainSet).sort()
  }, [job])

  // Filter recipients
  const filteredRecipients = useMemo(() => {
    if (!job) return []
    return job.recipients.filter((r) => {
      const matchesSearch = r.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.company?.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesDomain = !domainFilter || r.email.endsWith(`@${domainFilter}`)
      return matchesSearch && matchesDomain
    })
  }, [job, searchQuery, domainFilter])

  function toggleRecipient(email: string) {
    setSelectedRecipients((prev) => {
      const next = new Set(prev)
      if (next.has(email)) {
        next.delete(email)
      } else {
        next.add(email)
      }
      return next
    })
  }

  function selectAllFiltered() {
    setSelectedRecipients(new Set(filteredRecipients.map((r) => r.email)))
  }

  function clearSelection() {
    setSelectedRecipients(new Set())
  }

  async function handleSend() {
    if (!subject.trim() || !body.trim()) {
      toast({
        title: "Validation Error",
        description: "Please enter subject and body",
        variant: "destructive",
      })
      return
    }

    if (selectedRecipients.size === 0) {
      toast({
        title: "Validation Error",
        description: "Please select at least one recipient",
        variant: "destructive",
      })
      return
    }

    try {
      setSending(true)
      const result = await sendEmails(jobId, {
        subject,
        html_body: body,
        recipients: Array.from(selectedRecipients),
        dry_run: dryRun,
      })
      setSendResult(result)
      toast({
        title: "Success",
        description: dryRun ? "Dry run completed successfully" : "Emails sent successfully",
      })
      setTimeout(() => loadBatchStatus(), 1000)
    } catch (error: any) {
      console.error('Failed to send:', error)
      toast({
        title: "Error",
        description: error.message || 'Failed to send emails',
        variant: "destructive",
      })
    } finally {
      setSending(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-96" />
          <Skeleton className="h-96" />
        </div>
      </div>
    )
  }

  if (!job) {
    return null
  }

  const chartData = batchStatus ? [
    { name: 'Sent', value: batchStatus.sent },
    { name: 'Failed', value: batchStatus.failed },
    { name: 'Queued', value: batchStatus.queued },
  ] : []

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <motion.div whileHover={{ x: -4 }}>
            <Button
              variant="ghost"
              onClick={() => router.push('/')}
              className="mb-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </motion.div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
            {job.filename}
          </h1>
          <p className="text-muted-foreground mt-2">
            {job.recipient_count} recipients • Created {new Date(job.created_at).toLocaleString()}
          </p>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Recipients */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Recipients</CardTitle>
              <CardDescription>
                Search and filter recipients
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Search and Filters */}
              <div className="space-y-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Search emails, names, companies..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <select
                      value={domainFilter}
                      onChange={(e) => setDomainFilter(e.target.value)}
                      className="flex-1 w-full h-10 rounded-md border border-input bg-background px-3 py-2 pl-10 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <option value="">All Domains</option>
                      {domains.map((domain) => (
                        <option key={domain} value={domain}>
                          @{domain}
                        </option>
                      ))}
                    </select>
                  </div>
                  <Button
                    onClick={selectAllFiltered}
                    variant="outline"
                    size="sm"
                  >
                    Select All
                  </Button>
                  <Button
                    onClick={clearSelection}
                    variant="outline"
                    size="sm"
                  >
                    Clear
                  </Button>
                </div>
                <div className="text-sm text-muted-foreground">
                  {selectedRecipients.size} of {filteredRecipients.length} selected
                </div>
              </div>

              {/* Recipients Table */}
              <div className="border rounded-lg overflow-hidden max-h-96 overflow-y-auto">
                <table className="min-w-full divide-y divide-border">
                  <thead className="bg-muted/50 sticky top-0">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase w-12">
                        <input
                          type="checkbox"
                          checked={filteredRecipients.length > 0 && filteredRecipients.every((r) => selectedRecipients.has(r.email))}
                          onChange={(e) => {
                            if (e.target.checked) {
                              selectAllFiltered()
                            } else {
                              clearSelection()
                            }
                          }}
                          className="rounded border-gray-300"
                        />
                      </th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase">Email</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase">Name</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase">Company</th>
                    </tr>
                  </thead>
                  <tbody className="bg-background divide-y divide-border">
                    {filteredRecipients.map((recipient) => (
                      <tr
                        key={recipient.email}
                        className={`hover:bg-muted/50 transition-colors ${selectedRecipients.has(recipient.email) ? 'bg-primary/10' : ''}`}
                      >
                        <td className="px-4 py-2">
                          <input
                            type="checkbox"
                            checked={selectedRecipients.has(recipient.email)}
                            onChange={() => toggleRecipient(recipient.email)}
                            className="rounded border-gray-300"
                          />
                        </td>
                        <td className="px-4 py-2 text-sm">{recipient.email}</td>
                        <td className="px-4 py-2 text-sm text-muted-foreground">{recipient.name || '-'}</td>
                        <td className="px-4 py-2 text-sm text-muted-foreground">{recipient.company || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {filteredRecipients.length === 0 && (
                  <div className="p-8 text-center text-muted-foreground">No recipients match the filters</div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Right Column: Compose and Results */}
        <div className="space-y-6">
          {/* Compose Section */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Compose Email</CardTitle>
                <CardDescription>
                  Write your email content
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Subject</label>
                  <Input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="Email subject"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Body (HTML)</label>
                  <Textarea
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                    placeholder="<p>Your email body here...</p>"
                    rows={8}
                    className="font-mono text-sm"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="dry-run"
                    checked={dryRun}
                    onCheckedChange={setDryRun}
                  />
                  <label htmlFor="dry-run" className="text-sm font-medium">
                    Dry run (validate but don't send)
                  </label>
                </div>
                <Button
                  onClick={handleSend}
                  disabled={sending || selectedRecipients.size === 0}
                  className="w-full"
                >
                  {sending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    `Send to ${selectedRecipients.size} recipient${selectedRecipients.size !== 1 ? 's' : ''}`
                  )}
                </Button>
              </CardContent>
            </Card>
          </motion.div>

          {/* Preview Section */}
          {body && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Preview</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="border rounded-lg p-4 bg-muted/30">
                    <div className="text-sm font-medium mb-2">Subject: {subject || '(no subject)'}</div>
                    <div
                      className="prose max-w-none dark:prose-invert"
                      dangerouslySetInnerHTML={{ __html: body }}
                    />
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Results Section */}
          {(sendResult || batchStatus) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Send Results</CardTitle>
                    {sendResult?.batch_id && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={loadBatchStatus}
                      >
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {sendResult && (
                    <div className="space-y-2">
                      <div className="text-sm">
                        <span className="font-medium">Batch ID:</span> {sendResult.batch_id}
                      </div>
                      <div className="flex gap-4">
                        <Badge variant="success" className="gap-1">
                          <CheckCircle2 className="h-3 w-3" />
                          {sendResult.sent} sent
                        </Badge>
                        <Badge variant="destructive" className="gap-1">
                          <XCircle className="h-3 w-3" />
                          {sendResult.failed} failed
                        </Badge>
                        {sendResult.dry_run && (
                          <Badge variant="secondary" className="gap-1">
                            <Clock className="h-3 w-3" />
                            Dry Run
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}
                  {batchStatus && chartData.length > 0 && (
                    <div className="space-y-4">
                      <PieChartWrapper data={chartData} height={192} />
                      <div className="text-sm text-muted-foreground mb-2">Per-recipient status:</div>
                      <div className="max-h-64 overflow-y-auto border rounded-lg">
                        <table className="min-w-full divide-y divide-border">
                          <thead className="bg-muted/50">
                            <tr>
                              <th className="px-3 py-2 text-left text-xs font-medium text-muted-foreground">Email</th>
                              <th className="px-3 py-2 text-left text-xs font-medium text-muted-foreground">Status</th>
                            </tr>
                          </thead>
                          <tbody className="bg-background divide-y divide-border">
                            {batchStatus.results.map((result) => (
                              <tr key={result.email} className="hover:bg-muted/50">
                                <td className="px-3 py-2 text-sm">{result.email}</td>
                                <td className="px-3 py-2">
                                  <Badge
                                    variant={
                                      result.status === 'sent'
                                        ? 'success'
                                        : result.status === 'failed'
                                        ? 'destructive'
                                        : 'secondary'
                                    }
                                  >
                                    {result.status}
                                  </Badge>
                                  {result.error_message && (
                                    <div className="text-xs text-destructive mt-1">{result.error_message}</div>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
