# Fix: REDIS_URL Has PostgreSQL Connection String

## The Problem
Your `REDIS_URL` is set to a PostgreSQL connection string (`postgresql://...`) instead of a Redis connection string (`redis://...`).

This means you accidentally linked the **PostgreSQL service** instead of the **Redis service**.

## The Fix

### Step 1: Remove the Wrong REDIS_URL

1. **Go to worker service** (automail-worker)
2. **Go to "Variables" tab**
3. **Find `REDIS_URL`** (it should show it's referenced from PostgreSQL)
4. **Delete it** (click the three dots → Delete)

### Step 2: Find Your Actual Redis Service

1. **In Railway Dashboard**, look at all your services
2. **Find the Redis service** - it should have:
   - A database icon 🗄️
   - Name like "Redis" or "automail-redis"
   - **NOT** the PostgreSQL service

### Step 3: Get Redis Connection Info

**Option A: Check Redis Service Variables**

1. **Click on your Redis service** (NOT PostgreSQL)
2. **Go to "Variables" tab**
3. **Look for variables like:**
   - `REDIS_URL`
   - `REDISCLOUD_URL`
   - `DATABASE_URL` (might be used for Redis too)
   - Or connection-related variables

**Option B: Check Redis Service Connect Tab**

1. **Click on your Redis service**
2. **Go to "Connect" tab**
3. **Check "Public Network" tab**
4. **Look for connection info** - might show:
   - Host
   - Port
   - Password
   - Or a connection URL

### Step 4: Add Correct REDIS_URL

**If you find a Redis connection string:**

1. **Go to worker service** → **Variables** tab
2. **Click "+ New Variable"**
3. **Select "Raw Variable"**
4. **Set:**
   - **Name:** `REDIS_URL`
   - **Value:** The Redis connection string (must start with `redis://`)
5. **Click "Add"**

**If Railway doesn't provide a Redis connection string:**

You might need to use Railway's internal Redis or set up an external Redis service. Check if Railway actually created a Redis service, or if you need to add one.

### Step 5: Verify Services

Make sure you have:
- ✅ **PostgreSQL service** - for `DATABASE_URL`
- ✅ **Redis service** - for `REDIS_URL`

These should be **two separate services**!

---

## Quick Checklist

- [ ] Removed wrong `REDIS_URL` (the one with `postgresql://`)
- [ ] Found actual Redis service (separate from PostgreSQL)
- [ ] Got Redis connection string (starts with `redis://`)
- [ ] Added correct `REDIS_URL` to worker service
- [ ] Added correct `REDIS_URL` to backend service
- [ ] Added correct `REDIS_URL` to scheduler service

---

## Still Can't Find Redis?

If Railway doesn't have a Redis service:

1. **Create one:**
   - Click "+ New" → "Database" → "Redis"
2. **Wait for it to be created**
3. **Then follow Step 3 above** to get the connection string

---

## Verify It's Fixed

After setting the correct `REDIS_URL`:

1. **Redeploy worker service**
2. **Check logs** - Should see:
   - ✅ "Connected to Redis successfully"
   - ✅ No more "postgresql://" errors
