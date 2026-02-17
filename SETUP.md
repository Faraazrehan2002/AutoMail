# Setup Guide

## Environment Files

### Backend (`backend/.env`)

Create `backend/.env` with:

```env
# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=your_verified_sender@example.com

# Database
DATABASE_URL=sqlite:///./automail.db

# Rate Limiting
EMAILS_PER_SECOND=1.0

# Security
APP_API_KEY=your_secret_api_key_here

# CORS (comma-separated origins, or "*" for all)
ALLOWED_ORIGINS=http://localhost:3000

# Development
AUTO_MIGRATE_DEV=false
```

### Web (`web/.env`)

Create `web/.env` with:

```env
# Backend API URL (server-only, not exposed to browser)
BACKEND_API_BASE_URL=http://localhost:8000

# API Key (server-only, not exposed to browser)
APP_API_KEY=your_secret_api_key_here

# Public app name (safe to expose)
NEXT_PUBLIC_APP_NAME=AutoMail
```

**Important**: The `APP_API_KEY` in `web/.env` must match the one in `backend/.env`.

## Installation Steps

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies:**
   ```bash
   cd ../web
   npm install
   ```

3. **Install root dependencies (for concurrent dev):**
   ```bash
   cd ..
   npm install
   ```

4. **Set up environment files:**
   - Create `backend/.env` (see above)
   - Create `web/.env` (see above)

5. **Initialize database:**
   ```bash
   cd backend
   alembic upgrade head
   python scripts/db_check.py
   ```

6. **Run development servers:**
   ```bash
   # From root directory
   npm run dev
   ```

   Or separately:
   ```bash
   # Terminal 1
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2
   cd web
   npm run dev
   ```

## Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
