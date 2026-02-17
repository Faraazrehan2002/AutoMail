# 🚀 Start Here - AutoMail Full-Stack App

## Exact Commands to Run Locally

### Step 1: Install All Dependencies

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install Node.js dependencies
cd ../web
npm install

# Install root dependencies (for running both servers together)
cd ..
npm install
```

### Step 2: Create Environment Files

**Backend** (`backend/.env`):
```bash
cd backend
cat > .env << 'EOF'
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=your_verified_sender@example.com
DATABASE_URL=sqlite:///./automail.db
EMAILS_PER_SECOND=1.0
APP_API_KEY=some-long-random-string
ALLOWED_ORIGINS=http://localhost:3000
AUTO_MIGRATE_DEV=false
EOF
```

**Web** (`web/.env`):
```bash
cd ../web
cat > .env << 'EOF'
BACKEND_API_BASE_URL=http://localhost:8000
APP_API_KEY=some-long-random-string
NEXT_PUBLIC_APP_NAME=AutoMail
EOF
```

**⚠️ Important**: The `APP_API_KEY` value must be **identical** in both files!

### Step 3: Initialize Database

```bash
cd ../backend
alembic upgrade head
python scripts/db_check.py
```

Expected output: `✓ PASS - All checks passed`

### Step 4: Start Both Servers

**Run in separate terminals:**

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd web
npm run dev
```

This starts:
- ✅ Backend API on http://localhost:8000
- ✅ Next.js app on http://localhost:3000

**Note**: If you have `concurrently` installed, you can use `npm run dev` from root, but running separately works fine!

### Step 5: Open the App

Open your browser to: **http://localhost:3000**

## What You'll See

1. **Dashboard** (`/`):
   - Upload PDF button
   - Table of recent jobs

2. **Job Detail** (`/jobs/[jobId]`):
   - Recipients table with search/filter
   - Email composition form
   - Send results

3. **Batch Results** (`/batches/[jobId]/[batchId]`):
   - Detailed send status per recipient

## Troubleshooting

**Backend won't start:**
- Check `backend/.env` exists and has required values
- Verify Python dependencies: `pip install -r backend/requirements.txt`

**Frontend won't start:**
- Check `web/.env` exists
- Verify Node dependencies: `cd web && npm install`

**"Cannot connect to backend":**
- Ensure backend is running: `curl http://localhost:8000/health`
- Check `BACKEND_API_BASE_URL` in `web/.env`

**"401 Unauthorized":**
- Verify `APP_API_KEY` matches in both `.env` files

**Database errors:**
- Run: `cd backend && alembic upgrade head`

## Project Structure

```
AutoMail/
├── backend/          # FastAPI (Python)
│   ├── app/          # API code
│   ├── alembic/      # Migrations
│   └── .env          # Backend config
├── web/              # Next.js (TypeScript)
│   ├── app/          # Pages & API routes
│   └── .env          # Frontend config
└── package.json      # Root scripts
```

## Next Steps

1. Upload a PDF to test extraction
2. Select recipients and compose an email
3. Use dry_run=true first to test
4. Send real emails when ready

Enjoy! 🎉
