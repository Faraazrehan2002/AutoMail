# Fix Upstash Redis TLS Connection

## The Error
```
Connection closed by server
```

## The Problem
Upstash Redis requires TLS/SSL connections. The connection string might need to use `rediss://` (with double 's') instead of `redis://`.

## The Solution

### Option 1: Update Connection String (Easiest)

1. **Go to Upstash Dashboard** → Your Redis database
2. **Check the connection string** - it might show `redis://` but Upstash requires TLS
3. **Change `redis://` to `rediss://`** in your Railway variable:
   - Go to worker service → Variables
   - Edit `REDIS_URL`
   - Change `redis://` to `rediss://` at the start
   - Example: `rediss://default:password@host.upstash.io:6379`

### Option 2: Get Correct Connection String from Upstash

1. **Go to Upstash Dashboard**
2. **Click on your Redis database**
3. **Look for "Redis URL" or "Connection String"**
4. **Check if it shows:**
   - `redis://...` (non-TLS) - might not work
   - `rediss://...` (TLS) - this is what you need
5. **Copy the `rediss://` version** if available

### Option 3: Use Upstash REST API (Alternative)

If direct Redis connection doesn't work, Upstash also provides a REST API, but that would require code changes. The TLS fix above should work.

---

## Updated Code

I've updated the code to automatically try TLS (`rediss://`) if the regular connection fails. After you push this update:

1. **Push the code changes**
2. **Make sure your `REDIS_URL` uses `rediss://`** (with double 's')
3. **Redeploy worker service**

---

## Verify Connection String Format

Your `REDIS_URL` should look like:
```
rediss://default:password@xxx.upstash.io:6379
```

**Key points:**
- ✅ Starts with `rediss://` (double 's' = TLS)
- ✅ Has `default` as username
- ✅ Has password after colon
- ✅ Has `@host:port` format

---

## Still Not Working?

1. **Check Upstash dashboard** - Is the database active?
2. **Check IP allowlist** - Upstash might restrict by IP (Railway IPs should be allowed)
3. **Try creating a new Upstash database** - Sometimes a fresh database works better
4. **Check Upstash logs** - See if connection attempts are being logged

---

## Quick Fix Steps

1. **Go to worker service** → Variables → Edit `REDIS_URL`
2. **Change `redis://` to `rediss://`** at the start
3. **Save and redeploy**
4. **Check logs** - Should see "Connected to Redis with TLS successfully"
