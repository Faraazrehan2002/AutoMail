import type { Metadata } from 'next'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { Navbar } from '@/components/navbar'
import { Sidebar } from '@/components/sidebar'
import { Footer } from '@/components/footer'
import { Toaster } from '@/components/ui/toaster'
import { ErrorBoundary } from '@/components/error-boundary'
import { AuroraBackground } from '@/components/effects/aurora-background'
import { FluidCursor } from '@/components/effects/fluid-cursor'
import { AuthProvider } from '@/src/hooks/useAuth'

export const metadata: Metadata = {
  title: process.env.NEXT_PUBLIC_APP_NAME || 'AutoMail',
  description: 'PDF email extraction and sending service',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background text-foreground relative overflow-x-hidden">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {/* Animated background layers - wrapped in error boundary */}
          <ErrorBoundary>
            <AuroraBackground />
          </ErrorBoundary>
          
          {/* Fluid cursor effect - wrapped in error boundary */}
          <ErrorBoundary>
            <FluidCursor />
          </ErrorBoundary>
          
          {/* UI Content - always visible */}
          <AuthProvider>
            <div className="relative z-10 flex flex-col min-h-screen">
              <Navbar />
              <Sidebar />
              <main className="lg:ml-64 pt-16 flex-1">
                <div className="container mx-auto p-4 sm:p-6">
                  {children}
                </div>
              </main>
              <Footer />
              <Toaster />
            </div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
