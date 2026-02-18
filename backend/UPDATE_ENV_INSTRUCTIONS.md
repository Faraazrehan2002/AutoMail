# Update Your .env File

## Step 1: Edit backend/.env

Open `backend/.env` in a text editor and change:

**FROM:**
```env
FROM_EMAIL=faraazrehan2002@gmail.com
```

**TO:**
```env
FROM_EMAIL=mail@faraazrehan.com
```

## Step 2: Restart Services

After saving the file:

```bash
# Stop your current backend (Ctrl+C)
# Stop your current worker (Ctrl+C)

# Restart backend
cd backend
uvicorn app.main:app --reload

# Restart worker (in new terminal)
cd backend
python worker.py
```

## Step 3: Verify

```bash
cd backend
python scripts/check_sendgrid.py
```

Should show: `FROM_EMAIL is set: mail@faraazrehan.com`

## Step 4: Fix Failed DNS Records

Your SendGrid shows 2 failed DNS records. You need to:

1. **Go to SendGrid Dashboard:**
   - Settings → Sender Authentication
   - Click on `faraazrehan.com` domain
   - See which DNS records are missing

2. **Add Missing Records:**
   - Log in to your domain registrar (where you manage DNS)
   - Add ALL the CNAME records SendGrid shows
   - Make sure there are no typos

3. **Re-verify:**
   - Wait 24-48 hours for DNS to propagate
   - Click "Verify" again in SendGrid

## Step 5: Reduce Spam

After fixing DNS and updating FROM_EMAIL:
- Start with small batches (10-20 emails)
- Gradually increase over time
- Monitor SendGrid dashboard for reputation
