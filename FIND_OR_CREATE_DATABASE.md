# Find or Create PostgreSQL and Redis in Railway

## Step 1: Check if Services Already Exist

1. **Go to Railway Dashboard** (https://railway.app)
2. **Look at your project** - you should see a list of services
3. **Look for services named:**
   - Something like `Postgres` or `PostgreSQL` (database icon)
   - Something like `Redis` (database icon)
   - Or they might have auto-generated names

**If you see them:** Note their names and skip to Step 3.

**If you DON'T see them:** Continue to Step 2 to create them.

---

## Step 2: Create PostgreSQL Database

1. **In Railway Dashboard**, click **"+ New"** button (top right or in your project)
2. Select **"Database"**
3. Select **"PostgreSQL"**
4. Railway will create a PostgreSQL database
5. **Note the name** - it might be something like:
   - `Postgres`
   - `PostgreSQL`
   - Or an auto-generated name

**Wait for it to finish creating** (takes 1-2 minutes)

---

## Step 3: Create Redis Database

1. **Still in Railway Dashboard**, click **"+ New"** again
2. Select **"Database"**
3. Select **"Redis"**
4. Railway will create a Redis database
5. **Note the name** - it might be something like:
   - `Redis`
   - Or an auto-generated name

**Wait for it to finish creating** (takes 1-2 minutes)

---

## Step 4: Identify Your Services

After creating, your Railway project should show:

**Services List:**
```
📦 automail-backend
📦 automail-worker
📦 automail-scheduler
🗄️ Postgres (or PostgreSQL)
🗄️ Redis
```

The database services will have a **database icon** (🗄️) next to them.

---

## Step 5: Link Database to Backend

Now that you know which services are PostgreSQL and Redis:

### For Backend Service:

1. **Click on your backend service** (automail-backend)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Click **"Reference Variable"**
5. **Select your PostgreSQL service** from the dropdown (the one you just created/identified)
6. **Select `DATABASE_URL`** from the variable dropdown
7. Click **"Add"**

### Repeat for Redis:

1. Still in backend service → **Variables** tab
2. Click **"+ New Variable"**
3. Click **"Reference Variable"**
4. **Select your Redis service** from the dropdown
5. **Select `REDIS_URL`** from the variable dropdown
6. Click **"Add"**

---

## Step 6: Link to Worker and Scheduler

### For Worker Service:

1. **Click on worker service** (automail-worker)
2. Go to **"Variables"** tab
3. Add `DATABASE_URL` (reference from PostgreSQL)
4. Add `REDIS_URL` (reference from Redis)
5. Add `SENDGRID_API_KEY` (copy value from backend)
6. Add `FROM_EMAIL` (copy value from backend)

### For Scheduler Service:

1. **Click on scheduler service** (automail-scheduler)
2. Go to **"Variables"** tab
3. Add `DATABASE_URL` (reference from PostgreSQL)
4. Add `REDIS_URL` (reference from Redis)

---

## Visual Guide

Your Railway project should look like this:

```
┌─────────────────────────────────────┐
│  AutoMail Project                    │
├─────────────────────────────────────┤
│  📦 automail-backend                 │
│  📦 automail-worker                  │
│  📦 automail-scheduler               │
│  🗄️ Postgres ← This is PostgreSQL   │
│  🗄️ Redis ← This is Redis           │
└─────────────────────────────────────┘
```

---

## Still Can't Find Them?

### Option 1: Check All Services

1. In Railway Dashboard, look at the **left sidebar**
2. You should see all services listed
3. Database services have a **different icon** than application services

### Option 2: Create New Ones

If you're not sure which ones are yours:
1. **Create new PostgreSQL** (Step 2 above)
2. **Create new Redis** (Step 3 above)
3. Use these new ones (you can delete old ones later if needed)

### Option 3: Check Service Details

1. **Click on any service** that might be a database
2. Look at the **"Connect"** or **"Info"** tab
3. If it shows connection strings like `postgresql://...` → it's PostgreSQL
4. If it shows connection strings like `redis://...` → it's Redis

---

## Quick Checklist

After following this guide, you should have:

- [ ] PostgreSQL service created/identified
- [ ] Redis service created/identified
- [ ] `DATABASE_URL` linked in backend service
- [ ] `REDIS_URL` linked in backend service
- [ ] `DATABASE_URL` linked in worker service
- [ ] `REDIS_URL` linked in worker service
- [ ] `DATABASE_URL` linked in scheduler service
- [ ] `REDIS_URL` linked in scheduler service

---

## Next Steps

After linking the databases:
1. **Redeploy your services** (Railway auto-redeploys when variables change)
2. **Check logs** - should see database connection successful
3. **Check backend logs** - should see migrations running
4. **Test the API** - should work now!
