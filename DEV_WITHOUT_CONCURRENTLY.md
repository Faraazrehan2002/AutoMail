# Running Without Concurrently (If Disk Space is Low)

If you're getting "no space left on device" errors, you can run the servers separately without installing `concurrently`.

## Option 1: Run Separately (Recommended)

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd web
npm run dev
```

## Option 2: Install Only Web Dependencies

Skip root-level `npm install` and just install web dependencies:

```bash
cd web
npm install
```

Then run servers separately as shown above.

## Option 3: Clean Up Disk Space

If you need to free up space:

```bash
# Clean npm cache
npm cache clean --force

# Remove any existing node_modules
rm -rf node_modules
rm -rf web/node_modules

# Clean Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Remove old log files
rm -f *.log server.log

# Then try installing again
cd web && npm install
```

## Minimal Setup

You only need:
1. `cd web && npm install` (for Next.js)
2. `cd backend && pip install -r requirements.txt` (for FastAPI)

The root `package.json` with `concurrently` is optional - it's just a convenience for running both servers together.
