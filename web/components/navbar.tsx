"use client"

import Link from "next/link"
import { Mail } from "lucide-react"
import { ThemeToggle } from "./theme-toggle"
import { EffectsToggle } from "./effects-toggle"
import { motion } from "framer-motion"

export function Navbar() {
  return (
    <nav className="sticky top-0 z-40 w-full border-b border-border/40 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Link href="/" className="flex items-center gap-2 font-bold text-xl group">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
            >
              <Mail className="h-6 w-6 text-primary" />
            </motion.div>
            <span className="bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
              AutoMail
            </span>
          </Link>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          className="flex items-center gap-2"
        >
          <EffectsToggle />
          <ThemeToggle />
        </motion.div>
      </div>
    </nav>
  )
}
