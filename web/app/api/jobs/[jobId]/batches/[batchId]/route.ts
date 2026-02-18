import { NextRequest, NextResponse } from 'next/server'
import { getBackendHeaders, BACKEND_URL } from '../../../../_helpers'

export async function GET(
  request: NextRequest,
  { params }: { params: { jobId: string; batchId: string } }
) {
  try {
    const backendResponse = await fetch(
      `${BACKEND_URL}/jobs/${params.jobId}/batches/${params.batchId}`,
      {
        method: 'GET',
        headers: getBackendHeaders(),
      }
    )

    const data = await backendResponse.json()

    if (!backendResponse.ok) {
      return NextResponse.json(data, { status: backendResponse.status })
    }

    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to fetch batch' },
      { status: 500 }
    )
  }
}
