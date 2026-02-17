# Premium UI Upgrade Guide

Due to disk space constraints, follow these steps to complete the upgrade:

## Step 1: Install Dependencies

```bash
cd web
npm install lucide-react framer-motion next-themes recharts class-variance-authority clsx tailwind-merge @radix-ui/react-slot @radix-ui/react-toast @radix-ui/react-switch @radix-ui/react-dropdown-menu tailwindcss-animate
```

## Step 2: Create Required Files

Create these files manually (copy from the code blocks below):

### `/web/lib/utils.ts`
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### `/web/components/ui/button.tsx`
See: https://ui.shadcn.com/docs/components/button

### `/web/components/ui/toast.tsx` and related
See: https://ui.shadcn.com/docs/components/toast

### `/web/components/ui/switch.tsx`
See: https://ui.shadcn.com/docs/components/switch

### `/web/components/theme-provider.tsx`
```typescript
"use client"
import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes/dist/types"

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

### `/web/components/theme-toggle.tsx`
```typescript
"use client"
import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const { setTheme, theme } = useTheme()
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <Button variant="ghost" size="icon"><Sun className="h-4 w-4" /></Button>
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
    </Button>
  )
}
```

## Step 3: Update Existing Files

I'll provide the updated versions of existing files in separate messages due to length.

## Step 4: Update Tailwind Config

Update `tailwind.config.ts` with the full shadcn/ui configuration (see the code I attempted to write above).

## Step 5: Update globals.css

Replace with the shadcn/ui CSS variables setup.

## Next Steps

Once you free up disk space, I can complete all the file creations. For now, the key changes are:

1. **package.json** - Already updated with dependencies
2. **tailwind.config.ts** - Needs full shadcn config
3. **globals.css** - Needs CSS variables
4. **layout.tsx** - Needs ThemeProvider and new layout structure
5. **page.tsx** - Needs stats cards and modern design
6. **jobs/[jobId]/page.tsx** - Needs modern two-column layout

All API endpoints remain unchanged - only frontend UI is being upgraded.
