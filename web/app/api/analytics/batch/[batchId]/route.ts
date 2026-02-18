import { NextRequest, NextResponse } from 'next/server'
import { getBackendHeaders, BACKEND_URL } from '../../../_helpers'

export async function GET(
  request: NextRequest,
  { params }: { params: { batchId: string } }
) {
  try {
    const response = await fetch(`${BACKEND_URL}/analytics/batch/${params.batchId}`, {
      headers: getBackendHeaders(),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch batch analytics' }))
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to fetch batch analytics' },
      { status: 500 }
    )
  }
}
