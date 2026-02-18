import { NextRequest, NextResponse } from 'next/server'
import { getBackendHeaders, BACKEND_URL } from '../../_helpers'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const days = searchParams.get('days') || '30'

    const response = await fetch(`${BACKEND_URL}/analytics/overview?days=${days}`, {
      headers: getBackendHeaders(),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch analytics' }))
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to fetch analytics' },
      { status: 500 }
    )
  }
}
