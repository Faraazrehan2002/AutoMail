import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:8000'
const API_KEY = process.env.APP_API_KEY

export async function POST(
  request: NextRequest,
  { params }: { params: { jobId: string } }
) {
  try {
    const body = await request.json()

    const backendResponse = await fetch(
      `${BACKEND_URL}/jobs/${params.jobId}/send`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(API_KEY ? { 'X-APP-KEY': API_KEY } : {}),
        },
        body: JSON.stringify(body),
      }
    )

    const data = await backendResponse.json()

    if (!backendResponse.ok) {
      return NextResponse.json(data, { status: backendResponse.status })
    }

    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to send emails' },
      { status: 500 }
    )
  }
}
