# Quick Deployment Guide

This guide will help you deploy AutoMail to production in under 30 minutes.

## Prerequisites

- GitHub account (for connecting repositories)
- SendGrid account with API key
- Domain name (optional, but recommended)

## Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend) - RECOMMENDED ⭐

**Why this combo?**
- Vercel: Best-in-class Next.js hosting, free tier, automatic deployments
- Railway: Easy Python deployment, includes PostgreSQL and Redis, simple pricing

---

## Step-by-Step Deployment

### Part 1: Deploy Backend to Railway

1. **Sign up/Login to Railway**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your AutoMail repository
   - Select the `backend` folder as root directory

3. **Add PostgreSQL Database**
   - In your Railway project, click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically create a `DATABASE_URL` environment variable

4. **Add Redis**
   - Click "+ New" → "Database" → "Redis"
   - Railway will automatically create a `REDIS_URL` environment variable

5. **Configure Environment Variables**
   - Go to your backend service → "Variables" tab
   - Add these variables:
     ```
     SENDGRID_API_KEY=your_sendgrid_api_key_here
     FROM_EMAIL=your_verified_email@yourdomain.com
     APP_API_KEY=generate_a_random_secret_key_here
     JWT_SECRET_KEY=generate_another_random_secret_key_here
     ALLOWED_ORIGINS=https://your-frontend.vercel.app
     ```
   - **Important**: Replace placeholders with actual values
   - Generate secrets: `openssl rand -hex 32` (run in terminal)

6. **Set Build and Start Commands**
   - Go to "Settings" → "Deploy"
   - Build Command: `pip install -r requirements.txt && alembic upgrade head`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

7. **Deploy Worker**
   - Click "+ New" → "Empty Service"
   - Connect to same GitHub repo
   - Root directory: `backend`
   - Start Command: `python worker.py`
   - Copy all environment variables from main backend service

8. **Deploy Scheduler (Optional)**
   - Click "+ New" → "Empty Service"
   - Connect to same GitHub repo
   - Root directory: `backend`
   - Start Command: `python scheduler.py`
   - Copy environment variables (except SENDGRID_API_KEY and FROM_EMAIL if not needed)

9. **Get Backend URL**
   - Once deployed, Railway will give you a URL like: `https://your-app.up.railway.app`
   - Copy this URL - you'll need it for the frontend

---

### Part 2: Deploy Frontend to Vercel

1. **Sign up/Login to Vercel**
   - Go to https://vercel.com
   - Sign up with GitHub

2. **Import Project**
   - Click "Add New" → "Project"
   - Import your AutoMail repository
   - **Important**: Set "Root Directory" to `web`

3. **Configure Build Settings**
   - Framework Preset: Next.js (auto-detected)
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)
   - Install Command: `npm install` (default)

4. **Add Environment Variables**
   - Go to "Settings" → "Environment Variables"
   - Add these:
     ```
     BACKEND_API_BASE_URL=https://your-backend.railway.app
     APP_API_KEY=your_app_api_key_here (same as backend)
     NEXT_PUBLIC_APP_NAME=AutoMail
     ```
   - **Important**: Replace `your-backend.railway.app` with your actual Railway URL

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (2-5 minutes)
   - Vercel will give you a URL like: `https://your-app.vercel.app`

6. **Update Backend CORS**
   - Go back to Railway backend service
   - Update `ALLOWED_ORIGINS` to include your Vercel URL:
     ```
     ALLOWED_ORIGINS=https://your-app.vercel.app
     ```
   - Redeploy backend (Railway auto-redeploys on env var changes)

---

### Part 3: Test Deployment

1. **Visit your Vercel URL**
   - Should see the AutoMail login page

2. **Create an account**
   - Register a new user
   - Should work if backend is connected

3. **Upload a PDF**
   - Test the full flow
   - Check if emails are being sent

4. **Check Logs**
   - Railway: View logs in Railway dashboard
   - Vercel: View logs in Vercel dashboard
   - Check for any errors

---

## Alternative: Render Deployment

If you prefer Render over Railway:

1. **Sign up at https://render.com**

2. **Deploy Backend**
   - New → Web Service
   - Connect GitHub repo
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt && alembic upgrade head`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add PostgreSQL**
   - New → PostgreSQL
   - Render will provide `DATABASE_URL`

4. **Add Redis**
   - New → Redis
   - Render will provide `REDIS_URL`

5. **Deploy Worker**
   - New → Background Worker
   - Same settings as backend, but Start: `python worker.py`

6. **Deploy Frontend**
   - New → Static Site
   - Root Directory: `web`
   - Build: `npm run build`
   - Publish: `.next`

---

## Environment Variables Checklist

### Backend (Railway/Render)
- [ ] `DATABASE_URL` (auto-provided by PostgreSQL service)
- [ ] `REDIS_URL` (auto-provided by Redis service)
- [ ] `SENDGRID_API_KEY` (from SendGrid dashboard)
- [ ] `FROM_EMAIL` (your verified email)
- [ ] `APP_API_KEY` (generate random secret)
- [ ] `JWT_SECRET_KEY` (generate random secret)
- [ ] `ALLOWED_ORIGINS` (your Vercel URL)

### Frontend (Vercel)
- [ ] `BACKEND_API_BASE_URL` (your Railway/Render backend URL)
- [ ] `APP_API_KEY` (same as backend)
- [ ] `NEXT_PUBLIC_APP_NAME` (optional, defaults to "AutoMail")

---

## Custom Domain Setup

### Vercel (Frontend)
1. Go to project → Settings → Domains
2. Add your domain
3. Follow DNS instructions
4. Vercel will auto-configure SSL

### Railway (Backend)
1. Go to service → Settings → Networking
2. Add custom domain
3. Update DNS records
4. Railway will auto-configure SSL

**Important**: Update `ALLOWED_ORIGINS` in backend to include your custom domain!

---

## Troubleshooting

### Backend not connecting
- Check `BACKEND_API_BASE_URL` in Vercel matches Railway URL
- Check `ALLOWED_ORIGINS` includes Vercel URL
- Check Railway logs for errors

### Database errors
- Ensure migrations ran: Check Railway build logs
- Verify `DATABASE_URL` is set correctly

### Worker not processing
- Check worker service is running in Railway
- Check Redis connection
- View worker logs

### CORS errors
- Verify `ALLOWED_ORIGINS` includes exact frontend URL
- Check for trailing slashes
- Ensure protocol matches (https)

---

## Cost Estimate

### Free Tier (Hobby)
- **Vercel**: Free (generous limits)
- **Railway**: $5/month (includes $5 credit)
- **Total**: ~$5/month

### Production Tier
- **Vercel Pro**: $20/month
- **Railway**: $10-20/month (based on usage)
- **Total**: ~$30-40/month

---

## Next Steps After Deployment

1. ✅ Set up custom domain
2. ✅ Configure SendGrid domain authentication (for better deliverability)
3. ✅ Set up monitoring (Railway and Vercel have built-in monitoring)
4. ✅ Set up backups (Railway PostgreSQL has automatic backups)
5. ✅ Configure rate limiting if needed
6. ✅ Set up error tracking (Sentry, etc.)

---

## Support

If you encounter issues:
1. Check logs in Railway and Vercel dashboards
2. Verify all environment variables are set
3. Check that all services are running
4. Review the full DEPLOYMENT.md for detailed troubleshooting

---

**Congratulations! Your AutoMail app should now be live! 🎉**
