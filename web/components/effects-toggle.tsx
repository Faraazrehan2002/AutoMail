"use client"

import { useState, useEffect } from "react"
import { Sparkles, Power } from "lucide-react"
import { Button } from "./ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu"

export function EffectsToggle() {
  const [enabled, setEnabled] = useState(true)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    // Check localStorage
    const stored = localStorage.getItem("effects-enabled")
    if (stored !== null) {
      setEnabled(stored === "true")
    } else {
      // Default based on env var
      const defaultEnabled = process.env.NEXT_PUBLIC_EFFECTS !== "0" && process.env.NEXT_PUBLIC_EFFECTS !== "false"
      setEnabled(defaultEnabled)
    }
  }, [])

  const toggleEffects = (value: boolean) => {
    setEnabled(value)
    localStorage.setItem("effects-enabled", value.toString())
    // Reload to apply changes
    window.location.reload()
  }

  if (!mounted) {
    return null
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="w-9 h-9">
          {enabled ? (
            <Sparkles className="h-4 w-4" />
          ) : (
            <Power className="h-4 w-4 opacity-50" />
          )}
          <span className="sr-only">Toggle effects</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => toggleEffects(true)}>
          <Sparkles className="h-4 w-4 mr-2" />
          Enable Effects
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => toggleEffects(false)}>
          <Power className="h-4 w-4 mr-2" />
          Disable Effects
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
