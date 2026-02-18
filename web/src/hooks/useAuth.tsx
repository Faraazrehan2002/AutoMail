'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { login, register, refreshToken, type AuthResponse, type User } from '@/src/lib/api'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check for stored token on mount
    checkAuth()
  }, [])

  async function checkAuth() {
    try {
      // Check if we have a token in localStorage (fallback, prefer cookies)
      const token = localStorage.getItem('auth_token')
      if (token) {
        // Verify token by making a request
        const response = await fetch('/api/auth/me')
        if (response.ok) {
          const userData = await response.json()
          setUser(userData)
        } else {
          // Token invalid, clear it
          localStorage.removeItem('auth_token')
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error)
    } finally {
      setLoading(false)
    }
  }

  async function handleLogin(email: string, password: string) {
    try {
      const response = await login({ email, password })
      // Token is stored in httpOnly cookie by API route
      // Store user info if provided, otherwise create from email
      if (response.user) {
        setUser(response.user)
      } else {
        // Fallback: create user object from email
        setUser({ id: 'user', email })
      }
      // Also store token in localStorage as fallback (not ideal but works)
      localStorage.setItem('auth_token', response.access_token)
      router.push('/')
    } catch (error: any) {
      throw error
    }
  }

  async function handleRegister(email: string, password: string, fullName?: string) {
    try {
      const response = await register({ email, password, full_name: fullName })
      if (response.user) {
        setUser(response.user)
      } else {
        setUser({ id: 'user', email, full_name: fullName })
      }
      localStorage.setItem('auth_token', response.access_token)
      router.push('/')
    } catch (error: any) {
      throw error
    }
  }

  function handleLogout() {
    setUser(null)
    localStorage.removeItem('auth_token')
    // Call logout API to clear cookie
    fetch('/api/auth/logout', { method: 'POST' }).catch(console.error)
    router.push('/login')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
