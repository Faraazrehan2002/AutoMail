# Troubleshooting: Email Not Received

## Quick Checks

### 1. Is the Worker Running?

**The worker MUST be running for emails to be sent!**

Check if worker is running:
```bash
# In a new terminal, check if worker process exists
ps aux | grep "worker.py" | grep -v grep
```

If no worker is running, start it:
```bash
cd backend
python worker.py
```

You should see output like:
```
Starting RQ worker for 'emails' queue...
Connected to Redis: ...
```

### 2. Check Batch Status

From the logs, your batch ID is: `41f72afb-104d-43ce-a85d-a57f8e3a1fe9`

Check the batch status in the UI:
- Go to the job detail page
- Look at the "Send Results" section
- Check the status of each recipient

Or check via API:
```bash
curl http://localhost:8000/jobs/d63d717a-411f-48cf-b46a-0d36ff30124f/batches/41f72afb-104d-43ce-a85d-a57f8e3a1fe9 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Was it a Dry Run?

Check if "Dry run" was enabled when sending:
- If dry_run=true, emails are NOT actually sent
- They're only validated

### 4. Check SendGrid Configuration

Verify SendGrid is configured:
```bash
cd backend
python scripts/check_sendgrid.py
```

Common issues:
- ❌ SENDGRID_API_KEY not set
- ❌ FROM_EMAIL not verified in SendGrid
- ❌ API key doesn't have "Mail Send" permissions

### 5. Check Email Status

Possible statuses:
- **queued**: Waiting for worker to process
- **sending**: Currently being sent
- **sent**: Successfully sent (check SendGrid message ID)
- **failed**: Error occurred (check error_message)

### 6. Check Spam Folder

Even if status is "sent", the email might be in spam:
- Check spam/junk folder
- Verify FROM_EMAIL is authenticated in SendGrid
- Check SendGrid Activity Feed: https://app.sendgrid.com/activity

## Common Issues

### Issue: Status stuck on "queued"
**Solution**: Worker is not running. Start it with `python backend/worker.py`

### Issue: Status is "failed"
**Solution**: Check error_message in the batch results. Common errors:
- SendGrid API key invalid
- FROM_EMAIL not verified
- Rate limit exceeded

### Issue: Status is "sent" but no email received
**Solution**: 
1. Check spam folder
2. Verify recipient email is correct
3. Check SendGrid Activity Feed for delivery status
4. Verify FROM_EMAIL domain is authenticated

### Issue: Worker not processing jobs
**Solution**:
1. Check Redis is running: `redis-cli ping` (should return "PONG")
2. Check worker logs for errors
3. Restart worker: `python backend/worker.py`

## Next Steps

1. **Start the worker** (if not running):
   ```bash
   cd backend
   python worker.py
   ```

2. **Check the batch status** in the UI or via API

3. **Check SendGrid Activity Feed** to see delivery status

4. **Verify SendGrid configuration**:
   ```bash
   cd backend
   python scripts/check_sendgrid.py
   ```
