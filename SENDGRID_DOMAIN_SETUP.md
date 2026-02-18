# SendGrid Domain Authentication Setup for faraazrehan.com

This guide will help you set up SendGrid domain authentication for your domain `faraazrehan.com` to improve email deliverability and reduce spam filtering.

## Step 1: Set Up Domain Authentication in SendGrid

1. **Log in to SendGrid Dashboard**
   - Go to https://app.sendgrid.com
   - Navigate to **Settings** → **Sender Authentication**

2. **Authenticate Your Domain**
   - Click **Authenticate Your Domain**
   - Select your DNS provider (or choose "Other" if not listed)
   - Enter your domain: `faraazrehan.com`
   - Click **Next**

3. **Add DNS Records**
   - SendGrid will provide you with DNS records (CNAME records) to add
   - You'll need to add these records to your domain's DNS settings
   - Common records include:
     - `em1234.faraazrehan.com` → `u1234567.wl123.sendgrid.net`
     - `s1._domainkey.faraazrehan.com` → `s1.domainkey.u1234567.wl123.sendgrid.net`
     - `s2._domainkey.faraazrehan.com` → `s2.domainkey.u1234567.wl123.sendgrid.net`
     - (Exact records will be provided by SendGrid)

4. **Add Records to Your DNS Provider**
   - Log in to your domain registrar (where you bought faraazrehan.com)
   - Go to DNS Management / DNS Settings
   - Add each CNAME record provided by SendGrid
   - Save the changes

5. **Verify Domain in SendGrid**
   - Return to SendGrid dashboard
   - Click **Verify** or wait for automatic verification (can take up to 48 hours)
   - Once verified, you'll see a green checkmark

## Step 2: Update Your .env File

After domain authentication is verified, update your `backend/.env` file:

```env
FROM_EMAIL=noreply@faraazrehan.com
# Or use any subdomain:
# FROM_EMAIL=mail@faraazrehan.com
# FROM_EMAIL=hello@faraazrehan.com
```

**Important:** The email address must use your authenticated domain (`faraazrehan.com`).

## Step 3: Test Email Sending

1. Restart your backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Restart your worker (if running):
   ```bash
   cd backend
   python worker.py
   ```

3. Send a test email through the web interface

## Benefits of Domain Authentication

✅ **Improved Deliverability**: Emails are less likely to go to spam  
✅ **Branded Emails**: Emails appear to come from your domain  
✅ **Better Reputation**: Builds sender reputation for your domain  
✅ **SPF/DKIM Records**: Automatically configured for you  

## Troubleshooting

### Domain Not Verifying
- **Wait 24-48 hours**: DNS propagation can take time
- **Check DNS Records**: Ensure all CNAME records are correctly added
- **Check Record Values**: Make sure there are no typos in the target values
- **Use DNS Checker**: Use tools like `dig` or online DNS checkers to verify records

### Still Going to Spam
- **Warm Up Your Domain**: Start with small batches (10-20 emails/day)
- **Gradually Increase**: Increase volume over time
- **Monitor Reputation**: Check SendGrid dashboard for reputation metrics
- **Content Quality**: Ensure email content follows best practices

### Check DNS Records
```bash
# Check if CNAME records are set correctly
dig em1234.faraazrehan.com CNAME
dig s1._domainkey.faraazrehan.com CNAME
```

## Next Steps

1. ✅ Complete domain authentication in SendGrid
2. ✅ Update `FROM_EMAIL` in `.env` to use `@faraazrehan.com`
3. ✅ Test sending an email
4. ✅ Monitor deliverability in SendGrid dashboard

## Additional Resources

- [SendGrid Domain Authentication Guide](https://docs.sendgrid.com/ui/account-and-settings/how-to-set-up-domain-authentication)
- [SendGrid Best Practices](https://docs.sendgrid.com/ui/sending-email/best-practices)
- [Email Deliverability Guide](https://docs.sendgrid.com/ui/sending-email/deliverability)
