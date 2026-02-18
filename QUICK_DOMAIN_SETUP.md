# Quick Setup: Use mail@faraazrehan.com

## Step 1: Authenticate Your Domain in SendGrid

**Important:** You must authenticate your entire domain `faraazrehan.com` in SendGrid before you can use `mail@faraazrehan.com`.

### Steps:

1. **Go to SendGrid Dashboard**
   - Visit https://app.sendgrid.com
   - Navigate to **Settings** → **Sender Authentication**

2. **Authenticate Your Domain**
   - Click **"Authenticate Your Domain"** (NOT "Verify Single Sender")
   - Select your DNS provider (or "Other" if not listed)
   - Enter your domain: `faraazrehan.com`
   - Click **Next**

3. **Add DNS Records**
   - SendGrid will show you CNAME records to add
   - Example records you'll see:
     ```
     em1234.faraazrehan.com → u1234567.wl123.sendgrid.net
     s1._domainkey.faraazrehan.com → s1.domainkey.u1234567.wl123.sendgrid.net
     s2._domainkey.faraazrehan.com → s2.domainkey.u1234567.wl123.sendgrid.net
     ```
   - **Copy these exact records**

4. **Add Records to Your Domain's DNS**
   - Log in to where you manage your domain (e.g., Namecheap, GoDaddy, Cloudflare)
   - Go to DNS Management / DNS Settings
   - Add each CNAME record exactly as SendGrid provided
   - Save changes

5. **Verify in SendGrid**
   - Return to SendGrid dashboard
   - Click **"Verify"** or wait for automatic verification
   - ⏰ **This can take 24-48 hours** for DNS to propagate
   - You'll see a green checkmark when verified

## Step 2: Update Your .env File

Once your domain is verified, update `backend/.env`:

```env
FROM_EMAIL=mail@faraazrehan.com
```

## Step 3: Restart Services

After updating `.env`:

```bash
# Restart backend
cd backend
uvicorn app.main:app --reload

# Restart worker (in another terminal)
cd backend
python worker.py
```

## Step 4: Test

Send a test email - it should now come from `mail@faraazrehan.com`!

## Troubleshooting

### "Domain not verified" error
- Wait 24-48 hours for DNS propagation
- Double-check all CNAME records are added correctly
- Use `dig` command to verify records:
  ```bash
  dig em1234.faraazrehan.com CNAME
  ```

### Still getting 403 errors
- Make sure you authenticated the **domain**, not just a single sender
- Check that all DNS records are correct
- Verify domain shows as "Verified" in SendGrid dashboard

## Benefits

✅ Professional email address: `mail@faraazrehan.com`  
✅ Better deliverability (less spam)  
✅ Branded emails from your domain  
✅ Can use any address: `noreply@`, `hello@`, `contact@`, etc.
