import { NextRequest, NextResponse } from 'next/server'
import { getBackendHeaders, BACKEND_URL } from '../../_helpers'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    
    // Forward to backend with multipart/form-data
    const headers = getBackendHeaders()
    delete headers['Content-Type'] // Remove Content-Type for FormData
    
    const backendResponse = await fetch(`${BACKEND_URL}/attachments/upload`, {
      method: 'POST',
      headers,
      body: formData,
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
