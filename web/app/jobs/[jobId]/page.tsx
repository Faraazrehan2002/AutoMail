'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { getJob, sendEmails, getBatchStatus, type JobDetail, type SendResponse, type BatchStatus } from '@/src/lib/api'

export default function JobDetailPage() {
  const router = useRouter()
  const params = useParams()
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
      alert(error.message)
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
      alert('Please enter subject and body')
      return
    }

    if (selectedRecipients.size === 0) {
      alert('Please select at least one recipient')
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
      // Auto-load batch status
      setTimeout(() => loadBatchStatus(), 1000)
    } catch (error: any) {
      console.error('Failed to send:', error)
      alert(error.message || 'Failed to send emails')
    } finally {
      setSending(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (!job) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => router.push('/')}
            className="text-blue-600 hover:text-blue-800 mb-4"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">{job.filename}</h1>
          <p className="text-gray-500 mt-2">
            {job.recipient_count} recipients • Created {new Date(job.created_at).toLocaleString()}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Recipients */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Recipients</h2>

            {/* Search and Filters */}
            <div className="mb-4 space-y-3">
              <input
                type="text"
                placeholder="Search emails, names, companies..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <div className="flex gap-2">
                <select
                  value={domainFilter}
                  onChange={(e) => setDomainFilter(e.target.value)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Domains</option>
                  {domains.map((domain) => (
                    <option key={domain} value={domain}>
                      @{domain}
                    </option>
                  ))}
                </select>
                <button
                  onClick={selectAllFiltered}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                >
                  Select All
                </button>
                <button
                  onClick={clearSelection}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 text-sm"
                >
                  Clear
                </button>
              </div>
              <div className="text-sm text-gray-600">
                {selectedRecipients.size} of {filteredRecipients.length} selected
              </div>
            </div>

            {/* Recipients Table */}
            <div className="border border-gray-200 rounded-md overflow-hidden max-h-96 overflow-y-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase w-12">
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
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredRecipients.map((recipient) => (
                    <tr
                      key={recipient.email}
                      className={`hover:bg-gray-50 ${selectedRecipients.has(recipient.email) ? 'bg-blue-50' : ''}`}
                    >
                      <td className="px-4 py-2">
                        <input
                          type="checkbox"
                          checked={selectedRecipients.has(recipient.email)}
                          onChange={() => toggleRecipient(recipient.email)}
                          className="rounded border-gray-300"
                        />
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-900">{recipient.email}</td>
                      <td className="px-4 py-2 text-sm text-gray-500">{recipient.name || '-'}</td>
                      <td className="px-4 py-2 text-sm text-gray-500">{recipient.company || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredRecipients.length === 0 && (
                <div className="p-8 text-center text-gray-500">No recipients match the filters</div>
              )}
            </div>
          </div>

          {/* Right Column: Compose and Results */}
          <div className="space-y-6">
            {/* Compose Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Compose Email</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                  <input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="Email subject"
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Body (HTML)</label>
                  <textarea
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                    placeholder="<p>Your email body here...</p>"
                    rows={8}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                  />
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="dry-run"
                    checked={dryRun}
                    onChange={(e) => setDryRun(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <label htmlFor="dry-run" className="ml-2 text-sm text-gray-700">
                    Dry run (validate but don't send)
                  </label>
                </div>
                <button
                  onClick={handleSend}
                  disabled={sending || selectedRecipients.size === 0}
                  className={`w-full px-4 py-2 rounded-md font-medium ${
                    sending || selectedRecipients.size === 0
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {sending ? 'Sending...' : `Send to ${selectedRecipients.size} recipient${selectedRecipients.size !== 1 ? 's' : ''}`}
                </button>
              </div>
            </div>

            {/* Preview Section */}
            {body && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Preview</h2>
                <div className="border border-gray-200 rounded-md p-4 bg-gray-50">
                  <div className="text-sm font-medium text-gray-700 mb-2">Subject: {subject || '(no subject)'}</div>
                  <div
                    className="prose max-w-none"
                    dangerouslySetInnerHTML={{ __html: body }}
                  />
                </div>
              </div>
            )}

            {/* Results Section */}
            {(sendResult || batchStatus) && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold">Send Results</h2>
                  {sendResult?.batch_id && (
                    <button
                      onClick={loadBatchStatus}
                      className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                    >
                      Refresh
                    </button>
                  )}
                </div>
                {sendResult && (
                  <div className="mb-4 space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Batch ID:</span> {sendResult.batch_id}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Status:</span>{' '}
                      <span className="text-green-600">{sendResult.sent} sent</span>,{' '}
                      <span className="text-red-600">{sendResult.failed} failed</span>
                      {sendResult.dry_run && (
                        <span className="ml-2 text-yellow-600">(Dry Run)</span>
                      )}
                    </div>
                  </div>
                )}
                {batchStatus && (
                  <div className="space-y-2">
                    <div className="text-sm text-gray-600 mb-2">Per-recipient status:</div>
                    <div className="max-h-64 overflow-y-auto border border-gray-200 rounded-md">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Email</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Status</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {batchStatus.results.map((result) => (
                            <tr key={result.email}>
                              <td className="px-3 py-2 text-sm text-gray-900">{result.email}</td>
                              <td className="px-3 py-2">
                                <span
                                  className={`px-2 py-1 text-xs rounded-full ${
                                    result.status === 'sent'
                                      ? 'bg-green-100 text-green-800'
                                      : result.status === 'failed'
                                      ? 'bg-red-100 text-red-800'
                                      : 'bg-yellow-100 text-yellow-800'
                                  }`}
                                >
                                  {result.status}
                                </span>
                                {result.error_message && (
                                  <div className="text-xs text-red-600 mt-1">{result.error_message}</div>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
