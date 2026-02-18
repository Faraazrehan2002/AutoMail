"use client"

import { motion } from "framer-motion"
import { Heart } from "lucide-react"

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="relative z-10 border-t border-border/40 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60 lg:ml-64">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-2 text-xs sm:text-sm text-muted-foreground">
          <span>© {currentYear} AutoMail. All rights reserved.</span>
          <span className="hidden sm:inline">•</span>
          <div className="flex items-center gap-1.5">
            <span>Developed with</span>
            <motion.div
              animate={{ scale: [1, 1.15, 1] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
            >
              <Heart className="h-3.5 w-3.5 text-red-500 fill-red-500" />
            </motion.div>
            <span>by</span>
            <span className="font-medium text-foreground bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
              Faraaz Rehan
            </span>
          </div>
        </div>
      </div>
    </footer>
  )
}
