import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:8000'
const APP_API_KEY = process.env.APP_API_KEY || ''

export async function GET(
  request: NextRequest,
  { params }: { params: { jobId: string } }
) {
  try {
    const jobId = params.jobId

    const response = await fetch(`${BACKEND_URL}/jobs/${jobId}`, {
      headers: {
        'X-APP-KEY': APP_API_KEY,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Job not found' }))
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to fetch job' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { jobId: string } }
) {
  console.log('DELETE handler called for job:', params.jobId)
  console.log('Backend URL:', BACKEND_URL)
  console.log('API Key present:', !!APP_API_KEY)
  
  try {
    const jobId = params.jobId
    const backendUrl = `${BACKEND_URL}/jobs/${jobId}`
    console.log('Calling backend:', backendUrl)

    const response = await fetch(backendUrl, {
      method: 'DELETE',
      headers: {
        'X-APP-KEY': APP_API_KEY,
      },
    })

    console.log('Backend response status:', response.status)
    console.log('Backend response ok:', response.ok)

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete job' }))
      console.log('Backend error response:', error)
      return NextResponse.json(error, { status: response.status })
    }

    console.log('Delete successful, returning 204')
    return new NextResponse(null, { status: 204 })
  } catch (error: any) {
    console.error('Delete job error:', error)
    return NextResponse.json(
      { detail: error.message || 'Failed to delete job' },
      { status: 500 }
    )
  }
}
