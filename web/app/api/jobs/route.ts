import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:8000'
const API_KEY = process.env.APP_API_KEY

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const page = searchParams.get('page') || '1'
    const pageSize = searchParams.get('page_size') || '20'

    const backendResponse = await fetch(
      `${BACKEND_URL}/jobs?page=${page}&page_size=${pageSize}`,
      {
        method: 'GET',
        headers: API_KEY ? { 'X-APP-KEY': API_KEY } : {},
      }
    )

    const data = await backendResponse.json()

    if (!backendResponse.ok) {
      return NextResponse.json(data, { status: backendResponse.status })
    }

    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Failed to fetch jobs' },
      { status: 500 }
    )
  }
}
