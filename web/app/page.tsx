'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Upload, FileText, Calendar, Users, TrendingUp, Trash2, Loader2 } from 'lucide-react'
import { uploadPDF, listJobs, deleteJob, deleteAllJobs, type Job } from '@/src/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { StatsCard } from '@/components/stats-card'
import { useToast } from '@/hooks/use-toast'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

export default function Dashboard() {
  const router = useRouter()
  const { toast } = useToast()
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [deleting, setDeleting] = useState<string | null>(null)
  const [deletingAll, setDeletingAll] = useState(false)
  const pageSize = 20

  useEffect(() => {
    loadJobs()
  }, [page])

  async function loadJobs() {
    try {
      setLoading(true)
      const response = await listJobs(page, pageSize)
      setJobs(response.jobs)
      setTotal(response.total)
    } catch (error: any) {
      console.error('Failed to load jobs:', error)
      toast({
        title: "Error",
        description: error.message || "Failed to load jobs",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  async function handleFileUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.pdf')) {
      toast({
        title: "Invalid file",
        description: "Please upload a PDF file",
        variant: "destructive",
      })
      return
    }

    try {
      setUploading(true)
      const job = await uploadPDF(file)
      toast({
        title: "Success",
        description: "PDF uploaded and processed successfully",
      })
      router.push(`/jobs/${job.id}`)
    } catch (error: any) {
      console.error('Upload failed:', error)
      toast({
        title: "Upload failed",
        description: error.message || 'Upload failed',
        variant: "destructive",
      })
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  async function handleDeleteJob(jobId: string) {
    try {
      setDeleting(jobId)
      await deleteJob(jobId)
      toast({
        title: "Success",
        description: "Job deleted successfully",
      })
      // Reload jobs
      await loadJobs()
    } catch (error: any) {
      console.error('Failed to delete job:', error)
      toast({
        title: "Error",
        description: error.message || "Failed to delete job",
        variant: "destructive",
      })
    } finally {
      setDeleting(null)
    }
  }

  async function handleDeleteAll() {
    try {
      setDeletingAll(true)
      await deleteAllJobs()
      toast({
        title: "Success",
        description: "All jobs deleted successfully",
      })
      // Reload jobs
      await loadJobs()
    } catch (error: any) {
      console.error('Failed to delete all jobs:', error)
      toast({
        title: "Error",
        description: error.message || "Failed to delete all jobs",
        variant: "destructive",
      })
    } finally {
      setDeletingAll(false)
    }
  }

  const totalPages = Math.ceil(total / pageSize)
  const totalRecipients = jobs.reduce((sum, job) => sum + job.recipient_count, 0)

  return (
    <div className="space-y-8">
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Jobs"
          value={total}
          icon={FileText}
          description="All time jobs"
        />
        <StatsCard
          title="Total Recipients"
          value={totalRecipients}
          icon={Users}
          description="Across all jobs"
        />
        <StatsCard
          title="Success Rate"
          value={`${jobs.length > 0 ? Math.round((jobs.filter(job => job.recipient_count > 0).length / jobs.length) * 100) : 0}%`}
          icon={TrendingUp}
          description="Jobs with recipients"
        />
        <StatsCard
          title="Recent Activity"
          value={jobs.length > 0 ? new Date(jobs[0].created_at).toLocaleDateString() : 'None'}
          icon={Calendar}
          description="Last job created"
        />
      </div>

      {/* Upload Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Upload PDF</CardTitle>
            <CardDescription>
              Upload a PDF file to extract email addresses
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-muted-foreground/25 rounded-2xl p-12 text-center hover:border-primary/50 transition-colors">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
                id="pdf-upload"
              />
              <label
                htmlFor="pdf-upload"
                className="cursor-pointer flex flex-col items-center gap-4"
              >
                <div className={`rounded-full p-4 ${uploading ? 'bg-muted' : 'bg-primary/10'}`}>
                  <Upload className={`h-8 w-8 ${uploading ? 'text-muted-foreground' : 'text-primary'}`} />
                </div>
                <div>
                  <p className="text-lg font-semibold">
                    {uploading ? 'Processing PDF...' : 'Choose PDF File'}
                  </p>
                  <p className="text-sm text-muted-foreground mt-2">
                    {uploading ? 'Please wait while we extract emails' : 'Select a PDF file to extract email addresses'}
                  </p>
                </div>
                <Button
                  disabled={uploading}
                  className="mt-4"
                >
                  {uploading ? 'Uploading...' : 'Select File'}
                </Button>
              </label>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Jobs Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <CardTitle>Recent Jobs</CardTitle>
                <CardDescription>
                  View and manage your email extraction jobs
                </CardDescription>
              </div>
              {jobs.length > 0 && (
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="destructive"
                      size="sm"
                      disabled={deletingAll}
                    >
                      {deletingAll ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Deleting...
                        </>
                      ) : (
                        <>
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete All
                        </>
                      )}
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete All Jobs?</AlertDialogTitle>
                      <AlertDialogDescription>
                        This will permanently delete all {total} job(s) and their associated data (recipients, send logs, files). This action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction
                        onClick={handleDeleteAll}
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                      >
                        Delete All
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : jobs.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No jobs yet</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Upload a PDF to get started
                </p>
                <label htmlFor="pdf-upload">
                  <Button asChild>
                    <span>Upload PDF</span>
                  </Button>
                </label>
              </div>
            ) : (
              <>
                <div className="rounded-lg border border-border/40 overflow-hidden bg-card/50 backdrop-blur-sm">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-border/40">
                      <thead className="bg-muted/30 backdrop-blur-sm sticky top-0">
                        <tr>
                          <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                            Filename
                          </th>
                          <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                            Recipients
                          </th>
                          <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider hidden md:table-cell">
                            Created
                          </th>
                          <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-background/50 divide-y divide-border/40">
                        {jobs.map((job, index) => (
                          <motion.tr
                            key={job.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.05 }}
                            whileHover={{ 
                              x: 4
                            }}
                            className="relative group transition-all duration-200 hover:bg-primary/5"
                          >
                            {/* Shimmer effect on hover */}
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 animate-shimmer" />
                            <td className="px-3 sm:px-6 py-4 relative z-10">
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4 text-primary flex-shrink-0" />
                                <span className="text-sm font-medium break-words">{job.filename}</span>
                              </div>
                            </td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-muted-foreground relative z-10">
                              {job.recipient_count}
                            </td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-muted-foreground relative z-10 hidden md:table-cell">
                              {new Date(job.created_at).toLocaleString()}
                            </td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm font-medium relative z-10">
                              <div className="flex items-center gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => router.push(`/jobs/${job.id}`)}
                                  className="hover:bg-primary/10"
                                >
                                  View
                                </Button>
                                <AlertDialog>
                                  <AlertDialogTrigger asChild>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      disabled={deleting === job.id}
                                      className="hover:bg-destructive/10 hover:text-destructive"
                                    >
                                      {deleting === job.id ? (
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                      ) : (
                                        <Trash2 className="h-4 w-4" />
                                      )}
                                    </Button>
                                  </AlertDialogTrigger>
                                  <AlertDialogContent>
                                    <AlertDialogHeader>
                                      <AlertDialogTitle>Delete Job?</AlertDialogTitle>
                                      <AlertDialogDescription>
                                        This will permanently delete the job "{job.filename}" and all associated data (recipients, send logs, file). This action cannot be undone.
                                      </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                                      <AlertDialogAction
                                        onClick={() => handleDeleteJob(job.id)}
                                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                      >
                                        Delete
                                      </AlertDialogAction>
                                    </AlertDialogFooter>
                                  </AlertDialogContent>
                                </AlertDialog>
                              </div>
                            </td>
                          </motion.tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
                {totalPages > 1 && (
                  <div className="flex items-center justify-between mt-4">
                    <Button
                      variant="outline"
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      Previous
                    </Button>
                    <span className="text-sm text-muted-foreground">
                      Page {page} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
