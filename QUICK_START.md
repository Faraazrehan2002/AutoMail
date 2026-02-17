# Quick Start Guide

## Exact Commands to Run

### 1. Install Dependencies

```bash
# Python dependencies
cd backend
pip install -r requirements.txt

# Node.js dependencies  
cd ../web
npm install

# Root dependencies (for concurrent dev)
cd ..
npm install
```

### 2. Set Up Environment

**Create `backend/.env`:**
```bash
cd backend
cat > .env << 'EOF'
SENDGRID_API_KEY=your_key_here
FROM_EMAIL=your_email@example.com
DATABASE_URL=sqlite:///./automail.db
EMAILS_PER_SECOND=1.0
APP_API_KEY=some-long-random-string
ALLOWED_ORIGINS=http://localhost:3000
AUTO_MIGRATE_DEV=false
EOF
```

**Create `web/.env`:**
```bash
cd ../web
cat > .env << 'EOF'
BACKEND_API_BASE_URL=http://localhost:8000
APP_API_KEY=some-long-random-string
NEXT_PUBLIC_APP_NAME=AutoMail
EOF
```

**Important**: Use the same `APP_API_KEY` in both files!

### 3. Initialize Database

```bash
cd ../backend
alembic upgrade head
python scripts/db_check.py
```

### 4. Start Development Servers

**Option A: Concurrent (recommended)**
```bash
cd ..
npm run dev
```

**Option B: Separate terminals**
```bash
# Terminal 1
cd backend
uvicorn app.main:app --reload

# Terminal 2
cd web
npm run dev
```

### 5. Access the Application

- **Web UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Verify Everything Works

1. Open http://localhost:3000
2. Upload a PDF file
3. You should see extracted recipients
4. Select recipients and compose an email
5. Send (with dry_run=true first to test)

## Troubleshooting

**"Cannot connect to backend"**
- Check backend is running: `curl http://localhost:8000/health`
- Verify `BACKEND_API_BASE_URL` in `web/.env`

**"401 Unauthorized"**
- Check `APP_API_KEY` matches in both `.env` files
- Verify backend has `APP_API_KEY` set

**"Database errors"**
- Run: `cd backend && alembic upgrade head`
