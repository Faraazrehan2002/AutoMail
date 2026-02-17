# Fix react-is Package Error

## Problem
The `react-is` package (dependency of `recharts`) is missing or corrupted, causing build errors.

## Quick Fix

Run this command in the `web` directory:

```bash
cd web
rm -rf node_modules/react-is
npm install react-is
```

Or reinstall all dependencies:

```bash
cd web
rm -rf node_modules
npm install
```

## Alternative: Charts Made Optional

I've already made the charts optional in the code, so the app will work without recharts. The charts just won't display if the package is broken.

## If npm install fails due to disk space

Since your disk is full, you can:

1. **Delete node_modules and reinstall** (if you have space):
   ```bash
   cd web
   rm -rf node_modules
   npm install
   ```

2. **Or manually fix react-is**:
   ```bash
   cd web/node_modules/react-is
   # Check if package.json exists and has content
   # If not, delete the directory and reinstall
   ```

3. **Or disable charts temporarily**:
   The code now handles missing recharts gracefully - charts just won't show.

## Verify Fix

After fixing, restart the dev server:
```bash
npm run dev
```

The app should load without errors. Charts will appear if recharts is working, or the page will work without them if not.
