import { NextRequest, NextResponse } from 'next/server'
import { getBackendHeaders, BACKEND_URL } from '../_helpers'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = searchParams.get('page') || '1'
    const pageSize = searchParams.get('page_size') || '20'

    const response = await fetch(
      `${BACKEND_URL}/jobs?page=${page}&page_size=${pageSize}`,
      {
        headers: getBackendHeaders(),
      }
    )

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch jobs' }))
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to fetch jobs' },
      { status: 500 }
    )
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const response = await fetch(`${BACKEND_URL}/jobs`, {
      method: 'DELETE',
      headers: getBackendHeaders(),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete all jobs' }))
      return NextResponse.json(error, { status: response.status })
    }

    return new NextResponse(null, { status: 204 })
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to delete all jobs' },
      { status: 500 }
    )
  }
}
