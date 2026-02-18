'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { Search, Filter, CheckCircle2, XCircle, Clock, ArrowLeft, RefreshCw, Loader2, Calendar, FileText, Send } from 'lucide-react'
import { getJob, sendEmails, getBatchStatus, type JobDetail, type SendResponse, type BatchStatus, scheduleSend, type ScheduleRequest, listTemplates, type Template, uploadMultipleAttachments } from '@/src/lib/api'
import { useBatchProgress } from '@/src/hooks/useBatchProgress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
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
  const [attachments, setAttachments] = useState<File[]>([])
  const [attachmentPaths, setAttachmentPaths] = useState<string[]>([])
  const [uploadingAttachments, setUploadingAttachments] = useState(false)
  const [sending, setSending] = useState(false)
  const [sendResult, setSendResult] = useState<SendResponse | null>(null)
  const [batchStatus, setBatchStatus] = useState<BatchStatus | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [scheduledFor, setScheduledFor] = useState('')
  const [showSchedule, setShowSchedule] = useState(false)
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [loadingTemplates, setLoadingTemplates] = useState(false)
  
  // Use WebSocket hook for real-time progress
  const { progress, connected } = useBatchProgress(jobId, sendResult?.batch_id || null, !!sendResult?.batch_id)
  
  // Update batch status when WebSocket progress updates
  useEffect(() => {
    if (progress) {
      setBatchStatus({
        batch_id: progress.batch_id,
        job_id: progress.job_id,
        total_recipients: progress.total,
        queued: progress.remaining,
        sent: progress.sent,
        failed: progress.failed,
        created_at: progress.started_at || new Date().toISOString(),
        results: [], // Will be populated from full batch status
      })
    }
  }, [progress])

  useEffect(() => {
    loadJob()
    loadTemplates()
  }, [jobId])
  
  async function loadTemplates() {
    try {
      setLoadingTemplates(true)
      const data = await listTemplates()
      setTemplates(data)
    } catch (error) {
      console.error('Failed to load templates:', error)
    } finally {
      setLoadingTemplates(false)
    }
  }
  
  function handleTemplateSelect(templateId: string) {
    const template = templates.find(t => t.id === templateId)
    if (template) {
      setSelectedTemplate(templateId)
      setSubject(template.subject)
      // Convert HTML to plain text (remove tags, convert <br> to newlines)
      const plainText = template.html_body
        .replace(/<br\s*\/?>/gi, '\n')
        .replace(/<\/p>/gi, '\n\n')
        .replace(/<[^>]*>/g, '')
        .replace(/&nbsp;/g, ' ')
        .replace(/&amp;/g, '&')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&quot;/g, '"')
        .trim()
      setBody(plainText)
    }
  }

  useEffect(() => {
    if (sendResult?.batch_id) {
      loadBatchStatus()
      
      // Auto-refresh every 2 seconds
      const interval = setInterval(async () => {
        const batchId = sendResult?.batch_id
        if (!batchId) {
          clearInterval(interval)
          return
        }
        try {
          const status = await getBatchStatus(jobId, batchId)
          setBatchStatus(status)
          // Stop auto-refresh if batch is complete (all sent or failed, none queued)
          const isComplete = status.queued === 0 && (status.sent + status.failed === status.total_recipients)
          if (isComplete) {
            clearInterval(interval)
          }
        } catch (error) {
          // Silently fail for auto-refresh
          console.error('Auto-refresh error:', error)
        }
      }, 2000)
      
      return () => clearInterval(interval)
    }
  }, [sendResult?.batch_id, jobId])

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

  async function loadBatchStatus(showToast = false) {
    const batchId = sendResult?.batch_id
    if (!batchId) return
    
    setRefreshing(true)
    try {
      const status = await getBatchStatus(jobId, batchId)
      setBatchStatus(status)
      
      if (showToast) {
        toast({
          title: "Status Updated",
          description: `Sent: ${status.sent}, Failed: ${status.failed}, Queued: ${status.queued}`,
        })
      }
    } catch (error: any) {
      console.error('Failed to load batch status:', error)
      if (showToast) {
        toast({
          title: "Error",
          description: error.message || "Failed to load batch status",
          variant: "destructive",
        })
      }
    } finally {
      setRefreshing(false)
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
        body: body,
        recipients: Array.from(selectedRecipients),
        dry_run: dryRun,
        attachments: attachmentPaths.length > 0 ? attachmentPaths : undefined,
      })
      setSendResult(result)
      toast({
        title: "Success",
        description: dryRun ? "Dry run queued successfully" : "Emails queued successfully",
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
  
  async function handleSchedule() {
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

    if (!scheduledFor) {
      toast({
        title: "Validation Error",
        description: "Please select a date and time",
        variant: "destructive",
      })
      return
    }

    try {
      setSending(true)
      const result = await scheduleSend(jobId, {
        subject,
        body: body,
        recipients: Array.from(selectedRecipients),
        dry_run: dryRun,
        scheduled_for: scheduledFor,
        attachments: attachmentPaths.length > 0 ? attachmentPaths : undefined,
      })
      toast({
        title: "Success",
        description: `Emails scheduled for ${new Date(scheduledFor).toLocaleString()}`,
      })
      setShowSchedule(false)
      setScheduledFor('')
    } catch (error: any) {
      console.error('Failed to schedule:', error)
      toast({
        title: "Error",
        description: error.message || 'Failed to schedule emails',
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
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div className="flex-1 min-w-0">
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
          <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent truncate">
            {job.filename}
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground mt-2 break-words">
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
              <div className="border rounded-lg overflow-hidden max-h-96 overflow-y-auto overflow-x-auto">
                <table className="min-w-full divide-y divide-border">
                  <thead className="bg-muted/50 sticky top-0">
                    <tr>
                      <th className="px-2 sm:px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase w-12">
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
                      <th className="px-2 sm:px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase">Email</th>
                      <th className="px-2 sm:px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase hidden sm:table-cell">Name</th>
                      <th className="px-2 sm:px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase hidden md:table-cell">Company</th>
                    </tr>
                  </thead>
                  <tbody className="bg-background divide-y divide-border">
                    {filteredRecipients.map((recipient) => (
                      <tr
                        key={recipient.email}
                        className={`hover:bg-muted/50 transition-colors ${selectedRecipients.has(recipient.email) ? 'bg-primary/10' : ''}`}
                      >
                        <td className="px-2 sm:px-4 py-2">
                          <input
                            type="checkbox"
                            checked={selectedRecipients.has(recipient.email)}
                            onChange={() => toggleRecipient(recipient.email)}
                            className="rounded border-gray-300"
                          />
                        </td>
                        <td className="px-2 sm:px-4 py-2 text-sm break-words">{recipient.email}</td>
                        <td className="px-2 sm:px-4 py-2 text-sm text-muted-foreground hidden sm:table-cell">{recipient.name || '-'}</td>
                        <td className="px-2 sm:px-4 py-2 text-sm text-muted-foreground hidden md:table-cell">{recipient.company || '-'}</td>
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
                  <label className="block text-sm font-medium mb-2">Message Body</label>
                  <Textarea
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                    placeholder="Type your email message here. Line breaks will be preserved."
                    rows={10}
                    className="text-sm"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Plain text message. Line breaks will be converted to HTML automatically.
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Attachments (Resume, Cover Letter, etc.)</label>
                  <Input
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx"
                    onChange={async (e) => {
                      const files = Array.from(e.target.files || [])
                      if (files.length === 0) return
                      
                      setAttachments(files)
                      setUploadingAttachments(true)
                      
                      try {
                        // Upload files to server
                        const uploadResults = await uploadMultipleAttachments(files)
                        const paths = uploadResults.map(r => r.file_path)
                        setAttachmentPaths(paths)
                        toast({
                          title: "Success",
                          description: `Uploaded ${uploadResults.length} attachment(s)`,
                        })
                      } catch (error: any) {
                        console.error('Failed to upload attachments:', error)
                        toast({
                          title: "Upload Error",
                          description: error.message || 'Failed to upload attachments',
                          variant: "destructive",
                        })
                        setAttachments([])
                        setAttachmentPaths([])
                      } finally {
                        setUploadingAttachments(false)
                      }
                    }}
                    className="cursor-pointer"
                    disabled={uploadingAttachments}
                  />
                  {uploadingAttachments && (
                    <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Uploading attachments...</span>
                    </div>
                  )}
                  {attachments.length > 0 && !uploadingAttachments && (
                    <div className="mt-2 space-y-1">
                      {attachments.map((file, idx) => (
                        <div key={idx} className="text-sm text-muted-foreground flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          <span>{file.name}</span>
                          <span className="text-xs">({(file.size / 1024).toFixed(1)} KB)</span>
                          {attachmentPaths[idx] && (
                            <Badge variant="outline" className="text-xs">Uploaded</Badge>
                          )}
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="h-6 px-2 ml-auto"
                            onClick={() => {
                              const newAttachments = attachments.filter((_, i) => i !== idx)
                              const newPaths = attachmentPaths.filter((_, i) => i !== idx)
                              setAttachments(newAttachments)
                              setAttachmentPaths(newPaths)
                            }}
                          >
                            Remove
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground mt-1">
                    Upload PDF, DOC, or DOCX files to attach to your emails. Files are uploaded immediately when selected.
                  </p>
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
                    <div className="prose max-w-none dark:prose-invert whitespace-pre-wrap">
                      {body}
                    </div>
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
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div>
                      <CardTitle>Send Results</CardTitle>
                      {connected && (
                        <p className="text-xs text-muted-foreground mt-1">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse" />
                          Real-time updates active
                        </p>
                      )}
                    </div>
                    {sendResult?.batch_id && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => loadBatchStatus(true)}
                        disabled={refreshing}
                        className="w-full sm:w-auto"
                      >
                        <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                        {refreshing ? 'Refreshing...' : 'Refresh'}
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
                      {progress && (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>Progress</span>
                            <span className="font-medium">{progress.percent_complete.toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <div
                              className="bg-primary h-2 rounded-full transition-all duration-300"
                              style={{ width: `${progress.percent_complete}%` }}
                            />
                          </div>
                          <div className="flex gap-4 text-xs">
                            <span>Status: <Badge variant="secondary">{progress.status}</Badge></span>
                            <span>Remaining: {progress.remaining}</span>
                          </div>
                        </div>
                      )}
                      <div className="flex gap-4">
                        <Badge variant="success" className="gap-1">
                          <CheckCircle2 className="h-3 w-3" />
                          {progress?.sent || sendResult.sent || 0} sent
                        </Badge>
                        <Badge variant="destructive" className="gap-1">
                          <XCircle className="h-3 w-3" />
                          {progress?.failed || sendResult.failed || 0} failed
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
                      <div className="max-h-64 overflow-y-auto overflow-x-auto border rounded-lg">
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
