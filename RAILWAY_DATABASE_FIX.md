# Fix Railway Database Connection

## The Error
```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string ''
```

## The Problem
The `DATABASE_URL` environment variable is not set or is empty. Railway needs to link the PostgreSQL service to your backend service.

## The Solution

### Step 1: Add PostgreSQL Service (if not already added)

1. **In Railway Dashboard**, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will create a PostgreSQL database

### Step 2: Link Database to Backend Service

1. **Go to your backend service** (automail-backend)
2. Click on **"Variables"** tab
3. Look for **"DATABASE_URL"** - it should be there automatically
4. **If it's NOT there:**
   - Click **"+ New Variable"**
   - Click **"Reference Variable"**
   - Select your PostgreSQL service
   - Select **"DATABASE_URL"** from the dropdown
   - Click **"Add"**

### Step 3: Verify Environment Variables

Make sure these are set in your backend service:

- ✅ `DATABASE_URL` - Should be automatically set by Railway (from PostgreSQL service)
- ✅ `REDIS_URL` - Should be automatically set by Railway (from Redis service)
- ✅ `SENDGRID_API_KEY` - Your SendGrid API key
- ✅ `FROM_EMAIL` - Your verified email
- ✅ `APP_API_KEY` - Your secret key
- ✅ `JWT_SECRET_KEY` - Your JWT secret
- ✅ `ALLOWED_ORIGINS` - Your frontend URL

### Step 4: Link Database to Worker and Scheduler

**For Worker Service:**
1. Go to worker service → **Variables** tab
2. Add **"DATABASE_URL"** as a reference variable (same as backend)
3. Add **"REDIS_URL"** as a reference variable
4. Add **"SENDGRID_API_KEY"** and **"FROM_EMAIL"** (same values as backend)

**For Scheduler Service:**
1. Go to scheduler service → **Variables** tab
2. Add **"DATABASE_URL"** as a reference variable
3. Add **"REDIS_URL"** as a reference variable

### Step 5: Redeploy

After setting the variables:
1. **Redeploy all services** (or wait for auto-redeploy)
2. **Check logs** - Should see database connection successful
3. **Check migrations** - Should run automatically at startup

---

## Quick Check

To verify `DATABASE_URL` is set:

1. Go to backend service → **Variables** tab
2. Look for `DATABASE_URL`
3. It should show something like: `postgresql://postgres:password@host:5432/railway`

If it's empty or missing, follow Step 2 above.

---

## Alternative: Manual DATABASE_URL

If Railway doesn't automatically create the variable:

1. Go to PostgreSQL service → **Connect** tab
2. Copy the connection string
3. Go to backend service → **Variables** tab
4. Add new variable:
   - **Name:** `DATABASE_URL`
   - **Value:** Paste the connection string
5. Save and redeploy

---

## Still Having Issues?

1. **Check PostgreSQL service is running** - Should show "Active"
2. **Check database credentials** - In PostgreSQL service → Connect tab
3. **Verify variable name** - Must be exactly `DATABASE_URL` (case-sensitive)
4. **Check service linking** - Variables tab should show "Referenced from PostgreSQL"
