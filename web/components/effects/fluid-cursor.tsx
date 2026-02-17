"use client"

import { useEffect, useRef, useState } from "react"

interface Point {
  x: number
  y: number
}

export function FluidCursor() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationFrameRef = useRef<number>()
  const mouseRef = useRef<Point>({ x: 0, y: 0 })
  const targetRef = useRef<Point>({ x: 0, y: 0 })
  const trailRef = useRef<Point[]>([])
  const [isEnabled, setIsEnabled] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted || typeof window === "undefined") return

    // Check for reduced motion or mobile
    const prefersReducedMotion =
      window.matchMedia("(prefers-reduced-motion: reduce)").matches

    const isMobile =
      "ontouchstart" in window || navigator.maxTouchPoints > 0

    // Check localStorage for user preference
    const effectsEnabled =
      process.env.NEXT_PUBLIC_EFFECTS !== "0" &&
      process.env.NEXT_PUBLIC_EFFECTS !== "false" &&
      localStorage.getItem("effects-enabled") !== "false"

    if (prefersReducedMotion || isMobile || !effectsEnabled) {
      setIsEnabled(false)
      return
    }

    setIsEnabled(true)

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d", { alpha: true })
    if (!ctx) return

    const resize = () => {
      if (!canvas) return
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener("resize", resize)

    // Initialize trail
    const trailLength = 20
    for (let i = 0; i < trailLength; i++) {
      trailRef.current.push({ x: 0, y: 0 })
    }

    // Mouse move handler
    const handleMouseMove = (e: MouseEvent) => {
      targetRef.current = { x: e.clientX, y: e.clientY }
    }

    window.addEventListener("mousemove", handleMouseMove)

    // Spring physics for smooth following
    const spring = 0.15
    const friction = 0.8

    const animate = () => {
      if (!ctx || !canvas) return

      // Clear canvas completely (no black fill - this was causing blank screen)
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Update mouse position with spring physics
      const dx = targetRef.current.x - mouseRef.current.x
      const dy = targetRef.current.y - mouseRef.current.y
      mouseRef.current.x += dx * spring
      mouseRef.current.y += dy * spring

      // Update trail
      trailRef.current.unshift({ ...mouseRef.current })
      if (trailRef.current.length > trailLength) {
        trailRef.current.pop()
      }

      // Draw fluid trail
      ctx.globalCompositeOperation = "screen"
      trailRef.current.forEach((point, i) => {
        const progress = i / trailLength
        const size = Math.max(1, 30 * (1 - progress) * 0.5) // Ensure size is at least 1
        const opacity = (1 - progress) * 0.3

        // Skip if size is too small or opacity is too low
        if (size < 1 || opacity < 0.01) return

        // Create gradient for each point
        const gradient = ctx.createRadialGradient(
          point.x,
          point.y,
          0,
          point.x,
          point.y,
          size
        )
        gradient.addColorStop(0, `rgba(99, 102, 241, ${opacity})`)
        gradient.addColorStop(0.5, `rgba(139, 92, 246, ${opacity * 0.7})`)
        gradient.addColorStop(1, `rgba(99, 102, 241, 0)`)

        ctx.fillStyle = gradient
        ctx.beginPath()
        ctx.arc(point.x, point.y, size, 0, Math.PI * 2)
        ctx.fill()

        // Draw connecting lines for fluid effect
        if (i > 0) {
          const prev = trailRef.current[i - 1]
          const lineWidth = Math.max(0.5, 2 * (1 - progress))
          if (lineWidth > 0.5 && opacity > 0.01) {
            ctx.strokeStyle = `rgba(99, 102, 241, ${opacity * 0.2})`
            ctx.lineWidth = lineWidth
            ctx.beginPath()
            ctx.moveTo(prev.x, prev.y)
            ctx.lineTo(point.x, point.y)
            ctx.stroke()
          }
        }
      })

      ctx.globalCompositeOperation = "source-over"

      animationFrameRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (typeof window !== "undefined") {
        window.removeEventListener("resize", resize)
        window.removeEventListener("mousemove", handleMouseMove)
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [isEnabled, mounted])

  if (!mounted || !isEnabled) {
    return null
  }

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-20"
      style={{ 
        imageRendering: "auto",
        backgroundColor: "transparent"
      }}
    />
  )
}
