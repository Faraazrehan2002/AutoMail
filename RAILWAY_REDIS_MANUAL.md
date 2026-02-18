# Manual Redis URL Setup for Railway

## The Problem
Railway's Redis service might not expose `REDIS_URL` directly, or it might use a different variable name.

## Solution: Get Redis Connection String Manually

### Step 1: Find Your Redis Service

1. **Go to Railway Dashboard**
2. **Click on your Redis service** (the one with the database icon 🗄️)
3. **Look for one of these tabs:**
   - **"Connect"** tab
   - **"Info"** tab
   - **"Variables"** tab
   - **"Settings"** tab

### Step 2: Get Connection String

Look for connection information. Railway might show:

**Option A: Full Connection String**
```
redis://default:password@hostname:port
```

**Option B: Separate Values**
- Host: `something.upstash.io` or `host.railway.internal`
- Port: `6379` or `12345`
- Password: `some-password`
- Username: `default` (usually)

### Step 3: Build REDIS_URL

If Railway gives you separate values, build the URL like this:

**Format:**
```
redis://[username]:[password]@[host]:[port]
```

**Example:**
```
redis://default:my-password@redis-production.upstash.io:12345
```

**If no username:**
```
redis://:[password]@[host]:[port]
```

**If no password:**
```
redis://[host]:[port]
```

### Step 4: Add to Worker Service

1. **Go to worker service** (automail-worker)
2. **Go to "Variables" tab**
3. **Click "+ New Variable"**
4. **Select "Raw Variable"** (NOT "Reference Variable")
5. **Set:**
   - **Name:** `REDIS_URL`
   - **Value:** Paste the connection string you built
6. **Click "Add"**

### Step 5: Add to Other Services

Repeat Step 4 for:
- **Backend service** (automail-backend)
- **Scheduler service** (automail-scheduler)

---

## Alternative: Check Railway's Variable Names

Railway might use different variable names. Check your Redis service's "Variables" tab for:

- `REDIS_URL`
- `REDISCLOUD_URL`
- `UPSTASH_REDIS_REST_URL` (if using Upstash)
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_PASSWORD`

If you see different names, you can either:
1. **Use those values** to build your own `REDIS_URL`
2. **Or** set `REDIS_URL` manually using the connection string

---

## Common Railway Redis Formats

### Railway's Own Redis
Usually looks like:
```
redis://default:password@containers-us-west-xxx.railway.app:6379
```

### Upstash Redis (if Railway uses it)
Usually looks like:
```
redis://default:password@xxx.upstash.io:12345
```

---

## Verify It Works

After setting `REDIS_URL`:

1. **Redeploy worker service**
2. **Check logs** - Should see:
   - ✅ "Connected to Redis successfully"
   - ✅ "Starting RQ worker for 'emails' queue..."
3. **No more Redis URL errors**

---

## Still Can't Find It?

### Option 1: Check Redis Service Details
1. Click on Redis service
2. Look at all tabs (Connect, Info, Variables, Settings)
3. Look for any connection information

### Option 2: Use Railway CLI
If you have Railway CLI installed:
```bash
railway variables
```
This will show all variables for your project.

### Option 3: Check Service Logs
Sometimes Railway shows connection info in the service logs or startup messages.

---

## Quick Test

Once you set `REDIS_URL`, you can test it by checking the worker logs. If it connects successfully, you'll see:
```
Connected to Redis successfully
Starting RQ worker for 'emails' queue...
```

If you still see errors, the URL format might be wrong. Make sure it starts with `redis://`.
