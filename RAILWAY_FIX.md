# Railway Deployment Fix

## The Problem

Railway is detecting Node.js (from root `package.json`) instead of Python, so `pip` is not available during build.

## The Solution

### Option 1: Set Root Directory in Railway (RECOMMENDED ⭐)

**This is the BEST solution - do this first!**

1. **Go to each service in Railway** (backend, worker, scheduler)
2. **Go to Settings → Source**
3. **Set Root Directory to:** `backend`
4. **Save and redeploy**

This tells Railway to build from the `backend` folder where `requirements.txt` and `runtime.txt` are located, and it won't see the root `package.json`.

**Why this works:** Railway will only see Python files and won't try to install Node.js.

### Option 2: Use Dockerfile (Alternative)

If Option 1 doesn't work:

1. **Go to each service → Settings → Build**
2. **Change Builder to:** `Dockerfile`
3. **Set Dockerfile Path to:** `backend/Dockerfile`
4. **Save and redeploy**

### Option 3: Manual Build Command

If both options fail:

1. **Go to each service → Settings → Build**
2. **Set Build Command to:**
   ```bash
   cd backend && pip install -r requirements.txt && alembic upgrade head
   ```
3. **Set Start Command to:**
   ```bash
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. **Save and redeploy**

---

## For Worker Service

**Start Command:**
```bash
cd backend && python worker.py
```

## For Scheduler Service

**Start Command:**
```bash
cd backend && python scheduler.py
```

---

## Verify Fix

After applying the fix:

1. **Check build logs** - Should see Python packages installing
2. **Check deployment** - Should complete successfully
3. **Check service logs** - Should see application starting

---

## Still Having Issues?

1. **Check Railway logs** for specific error messages
2. **Verify `requirements.txt` exists** in `backend/` directory
3. **Verify `runtime.txt` exists** with `python-3.11`
4. **Check environment variables** are set correctly
5. **Ensure PostgreSQL and Redis services** are running
