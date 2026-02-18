# Fix Railway Start Command Error

## The Error
```
Container failed to start
The executable `cd` could not be found.
```

## The Problem
Railway is trying to execute a start command that includes `cd backend`, but when using Dockerfile with root directory set to `backend`, this is not needed and causes an error.

## The Solution

### For Backend Service:

1. **Go to Railway Dashboard** → Select your backend service
2. **Go to Settings → Deploy**
3. **Clear/Remove the Start Command** (leave it empty)
4. **Save**

The Dockerfile CMD will handle starting the server automatically.

### Alternative: If you must set a start command

If Railway requires a start command, set it to:
```bash
sh -c "alembic upgrade head || true && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

**Important:** Do NOT include `cd backend` - the working directory is already `/app` (which is the backend folder when root is set to `backend`).

---

### For Worker Service:

1. **Go to Settings → Deploy**
2. **Set Start Command to:**
   ```bash
   python worker.py
   ```
3. **Save**

### For Scheduler Service:

1. **Go to Settings → Deploy**
2. **Set Start Command to:**
   ```bash
   python scheduler.py
   ```
3. **Save**

---

## Verify

After clearing/updating the start command:

1. **Redeploy the service** (or wait for auto-redeploy)
2. **Check logs** - Should see migrations running, then server starting
3. **Check service status** - Should be "Running"

---

## Why This Happens

- When root directory is set to `backend`, Railway builds from that folder
- The Dockerfile WORKDIR is `/app`, which contains the backend code
- No need to `cd` anywhere - you're already in the right directory
- The Dockerfile CMD handles everything automatically
