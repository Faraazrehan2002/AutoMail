import { NextRequest, NextResponse } from 'next/server'
import { getBackendHeaders, BACKEND_URL } from '../../../../../_helpers'

export async function GET(
  request: NextRequest,
  { params }: { params: { jobId: string; batchId: string } }
) {
  try {
    const response = await fetch(
      `${BACKEND_URL}/jobs/${params.jobId}/batches/${params.batchId}/progress`,
      {
        headers: getBackendHeaders(),
      }
    )

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch progress' }))
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to fetch progress' },
      { status: 500 }
    )
  }
}
