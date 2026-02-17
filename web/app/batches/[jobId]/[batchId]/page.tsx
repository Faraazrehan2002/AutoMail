'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { getBatchStatus, type BatchStatus } from '@/src/lib/api'

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
      alert(error.message)
      router.push(`/jobs/${jobId}`)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (!batch) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => router.push(`/jobs/${jobId}`)}
            className="text-blue-600 hover:text-blue-800 mb-4"
          >
            ← Back to Job
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Batch Results</h1>
          <p className="text-gray-500 mt-2">
            Batch ID: {batch.batch_id} • Created {new Date(batch.created_at).toLocaleString()}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-6 grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{batch.total_recipients}</div>
              <div className="text-sm text-gray-500">Total</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{batch.sent}</div>
              <div className="text-sm text-gray-500">Sent</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{batch.failed}</div>
              <div className="text-sm text-gray-500">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{batch.queued}</div>
              <div className="text-sm text-gray-500">Queued</div>
            </div>
          </div>

          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Recipient Status</h2>
            <button
              onClick={loadBatch}
              className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Refresh
            </button>
          </div>

          <div className="border border-gray-200 rounded-md overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Message ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Error</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {batch.results.map((result) => (
                  <tr key={result.email} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{result.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
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
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {result.sendgrid_message_id || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-red-600">
                      {result.error_message || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
