import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { getBackendHeaders, BACKEND_URL } from '../../_helpers'

export async function GET(request: NextRequest) {
  try {
    const cookieStore = cookies()
    const token = cookieStore.get('auth_token')?.value

    if (!token) {
      return NextResponse.json({ detail: 'Not authenticated' }, { status: 401 })
    }

    // Call backend /auth/me endpoint
    const backendResponse = await fetch(`${BACKEND_URL}/auth/me`, {
      headers: getBackendHeaders(),
    })

    if (!backendResponse.ok) {
      return NextResponse.json({ detail: 'Invalid token' }, { status: 401 })
    }

    const userData = await backendResponse.json()
    return NextResponse.json(userData)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Auth check failed' },
      { status: 500 }
    )
  }
}
