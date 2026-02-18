# Deployment Checklist

Use this checklist to ensure everything is configured correctly before and after deployment.

## Pre-Deployment

### Backend Setup
- [ ] SendGrid API key obtained
- [ ] SendGrid sender email verified
- [ ] Random secret keys generated for `APP_API_KEY` and `JWT_SECRET_KEY`
- [ ] Backend code pushed to GitHub

### Frontend Setup
- [ ] Frontend code pushed to GitHub
- [ ] All dependencies installed locally (`npm install` in `web/` directory)

---

## Deployment Steps

### Step 1: Deploy Backend (Railway)

- [ ] Created Railway account
- [ ] Created new project from GitHub repo
- [ ] Set root directory to `backend`
- [ ] Added PostgreSQL database service
- [ ] Added Redis service
- [ ] Set environment variables:
  - [ ] `SENDGRID_API_KEY`
  - [ ] `FROM_EMAIL`
  - [ ] `APP_API_KEY` (generated secret)
  - [ ] `JWT_SECRET_KEY` (generated secret)
  - [ ] `ALLOWED_ORIGINS` (will update after frontend deploy)
- [ ] Set build command: `pip install -r requirements.txt && alembic upgrade head`
- [ ] Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Backend deployed successfully
- [ ] Backend URL copied: `https://________________.railway.app`
- [ ] Created worker service
- [ ] Worker start command: `python worker.py`
- [ ] Worker environment variables copied from backend
- [ ] Worker deployed successfully
- [ ] (Optional) Created scheduler service
- [ ] (Optional) Scheduler deployed successfully

### Step 2: Deploy Frontend (Vercel)

- [ ] Created Vercel account
- [ ] Imported project from GitHub
- [ ] Set root directory to `web`
- [ ] Set environment variables:
  - [ ] `BACKEND_API_BASE_URL` = `https://________________.railway.app`
  - [ ] `APP_API_KEY` = (same as backend)
  - [ ] `NEXT_PUBLIC_APP_NAME` = `AutoMail`
- [ ] Frontend deployed successfully
- [ ] Frontend URL copied: `https://________________.vercel.app`

### Step 3: Connect Frontend and Backend

- [ ] Updated backend `ALLOWED_ORIGINS` to include Vercel URL
- [ ] Backend redeployed (auto-redeploys on env var change)
- [ ] Verified CORS is working (no CORS errors in browser console)

---

## Post-Deployment Testing

### Basic Functionality
- [ ] Can access frontend URL
- [ ] Login page loads
- [ ] Can register new account
- [ ] Can login with registered account
- [ ] Dashboard loads
- [ ] Can upload PDF file
- [ ] PDF processing works (recipients extracted)
- [ ] Can compose email
- [ ] Can send email (dry run first)
- [ ] Email sending works (check SendGrid dashboard)
- [ ] Real-time progress updates work
- [ ] Batch results display correctly

### Advanced Features
- [ ] Templates page loads
- [ ] Can create template
- [ ] Can use template when composing
- [ ] Analytics page loads
- [ ] Analytics data displays
- [ ] Scheduling works (if implemented)
- [ ] File attachments work
- [ ] WebSocket connection works (real-time updates)

### Error Handling
- [ ] 404 pages work
- [ ] Error messages display correctly
- [ ] Network errors handled gracefully
- [ ] Invalid inputs show validation errors

---

## Production Hardening

### Security
- [ ] Strong `JWT_SECRET_KEY` set (32+ characters)
- [ ] Strong `APP_API_KEY` set (32+ characters)
- [ ] `ALLOWED_ORIGINS` set to specific domains (not `*`)
- [ ] HTTPS enabled (automatic on Vercel/Railway)
- [ ] Environment variables not exposed in client code
- [ ] API keys not in git repository

### Performance
- [ ] Database migrations completed
- [ ] Worker processing jobs correctly
- [ ] Redis connection working
- [ ] No memory leaks (monitor Railway usage)
- [ ] Frontend builds successfully
- [ ] Images/assets optimized

### Monitoring
- [ ] Railway logs accessible
- [ ] Vercel logs accessible
- [ ] Error tracking set up (optional: Sentry)
- [ ] Uptime monitoring set up (optional: UptimeRobot)

---

## Custom Domain (Optional)

### Frontend Domain
- [ ] Domain added to Vercel
- [ ] DNS records configured
- [ ] SSL certificate issued (automatic)
- [ ] Domain verified and working

### Backend Domain
- [ ] Domain added to Railway
- [ ] DNS records configured
- [ ] SSL certificate issued (automatic)
- [ ] `ALLOWED_ORIGINS` updated with custom domain

---

## Backup & Recovery

- [ ] Database backups enabled (Railway auto-backups)
- [ ] Backup restoration tested (optional)
- [ ] Environment variables documented (in secure location)
- [ ] Deployment process documented

---

## Notes

**Backend URL**: _________________________________________
**Frontend URL**: _________________________________________
**APP_API_KEY**: _________________________________________
**JWT_SECRET_KEY**: _________________________________________

**Deployment Date**: _________________________________________
**Deployed By**: _________________________________________

---

## Troubleshooting Log

| Issue | Solution | Date |
|-------|----------|------|
|       |          |      |
|       |          |      |
|       |          |      |

---

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete
