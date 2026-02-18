import { NextRequest, NextResponse } from 'next/server'
import { getBackendHeaders, BACKEND_URL } from '../_helpers'

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${BACKEND_URL}/templates`, {
      headers: getBackendHeaders(),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch templates' }))
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to fetch templates' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const response = await fetch(`${BACKEND_URL}/templates`, {
      method: 'POST',
      headers: getBackendHeaders(),
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create template' }))
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to create template' },
      { status: 500 }
    )
  }
}
