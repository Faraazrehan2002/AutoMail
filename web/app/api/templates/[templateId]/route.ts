import { NextRequest, NextResponse } from 'next/server'
import { getBackendHeaders, BACKEND_URL } from '../../_helpers'

export async function GET(
  request: NextRequest,
  { params }: { params: { templateId: string } }
) {
  try {
    const response = await fetch(`${BACKEND_URL}/templates/${params.templateId}`, {
      headers: getBackendHeaders(),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Template not found' }))
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to fetch template' },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { templateId: string } }
) {
  try {
    const body = await request.json()
    const response = await fetch(`${BACKEND_URL}/templates/${params.templateId}`, {
      method: 'PUT',
      headers: getBackendHeaders(),
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to update template' }))
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to update template' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { templateId: string } }
) {
  try {
    const response = await fetch(`${BACKEND_URL}/templates/${params.templateId}`, {
      method: 'DELETE',
      headers: getBackendHeaders(),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete template' }))
      return NextResponse.json(error, { status: response.status })
    }

    return new NextResponse(null, { status: 204 })
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to delete template' },
      { status: 500 }
    )
  }
}
