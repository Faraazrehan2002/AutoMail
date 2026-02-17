import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:8000'
const API_KEY = process.env.APP_API_KEY

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    
    // Forward to backend with multipart/form-data
    // Note: Don't set Content-Type header - fetch will set it with boundary
    const backendResponse = await fetch(`${BACKEND_URL}/upload`, {
      method: 'POST',
      headers: API_KEY ? { 'X-APP-KEY': API_KEY } : {},
      body: formData, // FormData automatically sets Content-Type with boundary
    })

    const data = await backendResponse.json()

    if (!backendResponse.ok) {
      return NextResponse.json(data, { status: backendResponse.status })
    }

    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Upload failed' },
      { status: 500 }
    )
  }
}
