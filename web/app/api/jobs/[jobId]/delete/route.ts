import { NextRequest, NextResponse } from 'next/server'
import { getBackendHeaders, BACKEND_URL } from '../../_helpers'

export async function POST(
  request: NextRequest,
  { params }: { params: { jobId: string } }
) {
  try {
    const jobId = params.jobId
    console.log('DELETE via POST workaround for job:', jobId)
    console.log('Backend URL:', `${BACKEND_URL}/jobs/${jobId}`)
    console.log('API Key present:', !!APP_API_KEY)

    const response = await fetch(`${BACKEND_URL}/jobs/${jobId}`, {
      method: 'DELETE',
      headers: getBackendHeaders(),
    })

    console.log('Backend response status:', response.status)
    console.log('Backend response ok:', response.ok)

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete job' }))
      console.log('Backend error:', error)
      return NextResponse.json(error, { status: response.status })
    }

    return new NextResponse(null, { status: 204 })
  } catch (error: any) {
    console.error('Delete job error:', error)
    return NextResponse.json(
      { detail: error.message || 'Failed to delete job' },
      { status: 500 }
    )
  }
}
