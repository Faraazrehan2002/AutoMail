"use client"

import { useEffect, useRef, useState } from "react"
import { useTheme } from "next-themes"

export function AuroraBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const { theme } = useTheme()
  const animationFrameRef = useRef<number>()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    // Check for reduced motion
    const prefersReducedMotion =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches

    if (prefersReducedMotion) {
      return
    }

    const canvas = canvasRef.current
    if (!canvas || typeof window === "undefined") return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const resize = () => {
      if (!canvas) return
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener("resize", resize)

    // Aurora gradient blobs
    const blobs: Array<{
      x: number
      y: number
      vx: number
      vy: number
      radius: number
      hue: number
    }> = []

    // Initialize blobs based on theme
    const isDark = theme === "dark"
    const baseHue = isDark ? 220 : 250
    const blobCount = 3

    for (let i = 0; i < blobCount; i++) {
      blobs.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: 200 + Math.random() * 300,
        hue: baseHue + (Math.random() - 0.5) * 30,
      })
    }

    let time = 0

    const animate = () => {
      if (!ctx || !canvas) return

      // Clear canvas completely first
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // Then draw with very subtle fade for trail effect (only if needed)
      // Using very low opacity to avoid black screen
      ctx.fillStyle = theme === "dark" ? "rgba(9, 9, 11, 0.02)" : "rgba(255, 255, 255, 0.02)"
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      time += 0.01

      // Update and draw blobs
      blobs.forEach((blob, i) => {
        // Update position with sine wave for smooth motion
        blob.x += blob.vx + Math.sin(time + i) * 0.5
        blob.y += blob.vy + Math.cos(time + i * 0.7) * 0.5

        // Wrap around edges
        if (blob.x < -blob.radius) blob.x = canvas.width + blob.radius
        if (blob.x > canvas.width + blob.radius) blob.x = -blob.radius
        if (blob.y < -blob.radius) blob.y = canvas.height + blob.radius
        if (blob.y > canvas.height + blob.radius) blob.y = -blob.radius

        // Draw gradient blob
        const gradient = ctx.createRadialGradient(
          blob.x,
          blob.y,
          0,
          blob.x,
          blob.y,
          blob.radius
        )

        const opacity = theme === "dark" ? 0.15 : 0.08
        gradient.addColorStop(0, `hsla(${blob.hue}, 70%, 60%, ${opacity})`)
        gradient.addColorStop(0.5, `hsla(${blob.hue + 20}, 60%, 50%, ${opacity * 0.5})`)
        gradient.addColorStop(1, `hsla(${blob.hue + 40}, 50%, 40%, 0)`)

        ctx.fillStyle = gradient
        ctx.beginPath()
        ctx.arc(blob.x, blob.y, blob.radius, 0, Math.PI * 2)
        ctx.fill()
      })

      animationFrameRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (typeof window !== "undefined") {
        window.removeEventListener("resize", resize)
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [theme, mounted])

  // Check for reduced motion or effects disabled
  const prefersReducedMotion =
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches

  const effectsEnabled =
    typeof window !== "undefined" &&
    (process.env.NEXT_PUBLIC_EFFECTS !== "0" && process.env.NEXT_PUBLIC_EFFECTS !== "false")

  if (!mounted || prefersReducedMotion || !effectsEnabled) {
    return null
  }

  return (
    <>
      <canvas
        ref={canvasRef}
        className="fixed inset-0 pointer-events-none z-0"
        style={{ 
          imageRendering: "auto",
          backgroundColor: "transparent"
        }}
      />
      {/* Subtle grid overlay */}
      <div
        className="fixed inset-0 pointer-events-none z-0 opacity-[0.03] dark:opacity-[0.05]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(0, 0, 0, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 0, 0, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: "50px 50px",
          backgroundColor: "transparent"
        }}
      />
    </>
  )
}
