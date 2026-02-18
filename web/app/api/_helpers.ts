import { NextRequest } from 'next/server'
import { cookies } from 'next/headers'

const BACKEND_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:8000'
const APP_API_KEY = process.env.APP_API_KEY || process.env.API_KEY || ''

export function getBackendHeaders(request?: NextRequest) {
  const cookieStore = cookies()
  const token = cookieStore.get('auth_token')?.value

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  // Add JWT token if available
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Add API key if configured
  if (APP_API_KEY) {
    headers['X-APP-KEY'] = APP_API_KEY
  }

  return headers
}

export { BACKEND_URL, APP_API_KEY }
