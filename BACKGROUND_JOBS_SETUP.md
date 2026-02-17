# Background Job Processing - Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Redis
```bash
# Option A: Docker (Recommended)
docker-compose up -d redis

# Option B: Local
redis-server
```

### 3. Run Database Migration
```bash
cd backend
alembic upgrade head
```

### 4. Start Services

**Terminal 1 - Backend API:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 - Background Worker (Required!):**
```bash
cd backend
python worker.py
```

**Terminal 3 - Frontend:**
```bash
cd web
npm run dev
```

## How It Works

1. **POST /jobs/{job_id}/send** - Enqueues emails and returns immediately with `batch_id`
2. **Worker** processes emails sequentially with rate limiting
3. **Progress** can be tracked via `GET /jobs/{job_id}/batches/{batch_id}/progress`
4. **Status** updates in real-time: `queued` → `sending` → `sent`/`failed`

## API Changes

### POST /jobs/{job_id}/send
- **Before**: Sent emails synchronously, returned results immediately
- **After**: Enqueues job, returns immediately with `status="queued"`

### New: GET /jobs/{job_id}/batches/{batch_id}/progress
Returns:
```json
{
  "total": 100,
  "sent": 45,
  "failed": 2,
  "remaining": 53,
  "percent_complete": 47.0,
  "status": "processing"
}
```

Status values:
- `"queued"` - Batch is waiting to be processed
- `"processing"` - Emails are being sent
- `"completed"` - All emails processed

## Worker Features

- ✅ Sequential processing with rate limiting
- ✅ Progress tracking per recipient
- ✅ Crash recovery (queued emails remain queued)
- ✅ Individual error handling
- ✅ Dry run support

## Troubleshooting

### "Failed to connect to Redis"
- Ensure Redis is running: `redis-cli ping` should return `PONG`
- Check `REDIS_URL` in `backend/.env` (default: `redis://localhost:6379/0`)

### "No emails being sent"
- **Worker must be running!** Check Terminal 2
- Verify Redis connection
- Check worker logs for errors

### "Worker crashes"
- Queued emails remain in database with `status="queued"`
- Restart worker to continue processing
- Failed emails have `status="failed"` with error message

## Environment Variables

Add to `backend/.env`:
```env
REDIS_URL=redis://localhost:6379/0
```

## Testing

1. Upload a PDF and extract recipients
2. Send emails - should return immediately with `batch_id`
3. Poll `/jobs/{job_id}/batches/{batch_id}/progress` to see progress
4. Check `/jobs/{job_id}/batches/{batch_id}` for final results
