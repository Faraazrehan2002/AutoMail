'use client'

import { useState, useEffect, useRef } from 'react'
import { getBatchProgress, type BatchProgressResponse } from '@/src/lib/api'

export function useBatchProgress(jobId: string, batchId: string | null, enabled: boolean = true) {
  const [progress, setProgress] = useState<BatchProgressResponse | null>(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!enabled || !batchId) return

    // Try WebSocket first - connect directly to backend
    // In production, you might want to proxy through Next.js or use a service
    let backendWsUrl: string
    if (typeof window !== 'undefined') {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsHost = process.env.NEXT_PUBLIC_WS_URL 
        ? process.env.NEXT_PUBLIC_WS_URL.replace(/^https?:/, wsProtocol === 'wss:' ? 'wss:' : 'ws:')
        : `${wsProtocol}//${window.location.hostname}:8000`
      backendWsUrl = `${wsHost}/ws/jobs/${jobId}/batches/${batchId}`
    } else {
      backendWsUrl = `ws://localhost:8000/ws/jobs/${jobId}/batches/${batchId}`
    }
    
    try {
      const ws = new WebSocket(backendWsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setConnected(true)
        setError(null)
        // Clear polling if WebSocket connects
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current)
          pollIntervalRef.current = null
        }
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'progress') {
            setProgress(data)
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }

      ws.onerror = () => {
        setConnected(false)
        // Fallback to polling
        startPolling()
      }

      ws.onclose = () => {
        setConnected(false)
        // Fallback to polling
        startPolling()
      }

      return () => {
        ws.close()
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current)
        }
      }
    } catch (e) {
      // WebSocket not available, use polling
      startPolling()
    }

    function startPolling() {
      // Poll every 2 seconds
      pollIntervalRef.current = setInterval(async () => {
        try {
          const data = await getBatchProgress(jobId, batchId!)
          setProgress(data)
          setError(null)
          
          // Stop polling if batch is complete
          if (data.status === 'completed' || data.status === 'failed') {
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current)
              pollIntervalRef.current = null
            }
          }
        } catch (err: any) {
          setError(err.message)
        }
      }, 2000)
    }

    // Initial fetch
    getBatchProgress(jobId, batchId).then(setProgress).catch(setError)

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
      }
    }
  }, [jobId, batchId, enabled])

  return { progress, connected, error }
}
