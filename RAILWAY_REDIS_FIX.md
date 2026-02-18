# Fix Worker Redis Connection Error

## The Error
```
ValueError: Redis URL must specify one of the following schemes (redis://, rediss://, unix://)
```

## The Problem
The `REDIS_URL` environment variable is either:
- Not set in the worker service
- Set but empty
- Set with an invalid format

## The Solution

### Step 1: Check Redis Service Exists

1. **Go to Railway Dashboard**
2. **Look for a Redis service** (should have a database icon 🗄️)
3. **If you don't see one**, create it:
   - Click "+ New" → "Database" → "Redis"

### Step 2: Link REDIS_URL to Worker Service

1. **Go to your worker service** (automail-worker)
2. **Click on "Variables" tab**
3. **Look for `REDIS_URL`**:
   - **If it exists but is empty** → Delete it and re-add it
   - **If it doesn't exist** → Continue below

4. **Click "+ New Variable"**
5. **Click "Reference Variable"**
6. **Select your Redis service** from the dropdown
7. **Select `REDIS_URL`** from the variable dropdown
8. **Click "Add"**

### Step 3: Verify REDIS_URL Format

The `REDIS_URL` should look like one of these:
- `redis://default:password@host:port`
- `rediss://default:password@host:port` (SSL)
- `redis://host:port` (no auth)

**It MUST start with `redis://` or `rediss://`**

### Step 4: Check Other Services

Make sure these services also have `REDIS_URL`:
- ✅ **Backend service** - Should have `REDIS_URL`
- ✅ **Worker service** - Should have `REDIS_URL` (this is the one failing)
- ✅ **Scheduler service** - Should have `REDIS_URL`

### Step 5: Redeploy Worker

After setting the variable:
1. **Redeploy the worker service** (or wait for auto-redeploy)
2. **Check logs** - Should see Redis connection successful
3. **Worker should start processing jobs**

---

## Quick Checklist

- [ ] Redis service exists in Railway
- [ ] `REDIS_URL` is linked in worker service (as reference variable)
- [ ] `REDIS_URL` starts with `redis://` or `rediss://`
- [ ] Worker service redeployed
- [ ] Worker logs show successful Redis connection

---

## Alternative: Manual REDIS_URL

If Railway doesn't automatically create the variable:

1. **Go to Redis service** → **"Connect"** or **"Info"** tab
2. **Copy the connection string** (should start with `redis://`)
3. **Go to worker service** → **"Variables"** tab
4. **Add new variable:**
   - **Name:** `REDIS_URL`
   - **Value:** Paste the connection string
5. **Save and redeploy**

---

## Verify It's Working

After fixing, check worker logs. You should see:
- ✅ "Connected to Redis"
- ✅ "Worker started"
- ✅ No more Redis URL errors

---

## Still Having Issues?

1. **Check Redis service is running** - Should show "Active"
2. **Verify variable name** - Must be exactly `REDIS_URL` (case-sensitive)
3. **Check connection string format** - Must start with `redis://`
4. **Verify service linking** - Variables tab should show "Referenced from Redis"
