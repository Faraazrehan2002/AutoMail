# AutoMail - Full-Stack Application

A production-ready full-stack application for extracting email addresses from PDFs and sending emails via SendGrid.

## Architecture

- **Backend**: FastAPI (Python) - REST API for PDF processing and email sending
- **Frontend**: Next.js 14+ (TypeScript) - Modern web UI with App Router
- **Database**: SQLite with SQLAlchemy 2.0 and Alembic migrations

## Project Structure

```
AutoMail/
├── backend/          # FastAPI application
│   ├── app/         # Main application code
│   ├── alembic/     # Database migrations
│   ├── scripts/     # Utility scripts
│   └── tests/       # Test suite
├── web/             # Next.js application
│   ├── app/         # App Router pages and API routes
│   └── src/lib/     # API client and utilities
└── README.md        # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- SendGrid API key
- Verified sender email address

### 1. Install Dependencies

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install Node.js dependencies
cd ../web
npm install

# Install root dependencies (for concurrent dev)
cd ..
npm install
```

### 2. Configure Environment

**Backend** (`backend/.env`):
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your SendGrid credentials
```

**Web** (`web/.env`):
```bash
cp web/.env.example web/.env
# Edit web/.env with backend URL and API key
```

### 3. Initialize Database

```bash
cd backend
alembic upgrade head
python scripts/db_check.py
```

### 4. Run Development Servers

**Run in separate terminals (recommended):**

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd web
npm run dev
```

This starts:
- Backend API: http://localhost:8000
- Next.js app: http://localhost:3000

**Alternative**: If you have `concurrently` installed, you can use `npm run dev` from root directory.

## Features

### Web UI

- **Dashboard** (`/`): Upload PDFs and view recent jobs
- **Job Detail** (`/jobs/[jobId]`):
  - Recipients table with search and domain filtering
  - Select recipients with checkboxes
  - Compose email with subject and HTML body
  - Live preview
  - Dry run mode
  - View send results
- **Batch Results** (`/batches/[jobId]/[batchId]`): Detailed batch status

### Backend API

- `POST /upload` - Upload PDF and extract emails
- `GET /jobs` - List jobs (paginated)
- `GET /jobs/{job_id}` - Get job details
- `POST /jobs/{job_id}/send` - Send emails
- `GET /jobs/{job_id}/batches/{batch_id}` - Get batch status
- `GET /health` - Health check

## API Proxy Layer

The Next.js app includes API route handlers (`web/app/api/*`) that proxy requests to the FastAPI backend. This:

- Keeps API keys server-side (never exposed to browser)
- Avoids CORS issues
- Allows future migration of logic to Next.js
- Provides a unified API surface

Frontend code should **only** call `/api/*` routes, never the FastAPI backend directly.

## Environment Variables

### Backend (`backend/.env`)

```env
SENDGRID_API_KEY=your_key
FROM_EMAIL=your_verified_email@example.com
DATABASE_URL=sqlite:///./automail.db
EMAILS_PER_SECOND=1.0
APP_API_KEY=your_secret_key
ALLOWED_ORIGINS=http://localhost:3000
```

### Web (`web/.env`)

```env
BACKEND_API_BASE_URL=http://localhost:8000
APP_API_KEY=your_secret_key
NEXT_PUBLIC_APP_NAME=AutoMail
```

**Important**: 
- `APP_API_KEY` in web/.env must match backend/.env
- Never use `NEXT_PUBLIC_` prefix for secrets
- These are server-only variables (not exposed to browser)

## Development

### Backend

```bash
cd backend

# Run migrations
alembic upgrade head

# Run tests
pytest

# Check database schema
python scripts/db_check.py
```

### Frontend

```bash
cd web

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Production Deployment

### Backend

1. Set up production database (PostgreSQL recommended)
2. Configure environment variables
3. Run migrations: `alembic upgrade head`
4. Run with production ASGI server (e.g., Gunicorn + Uvicorn)

### Frontend

1. Build: `npm run build`
2. Deploy to Vercel, Netlify, or similar
3. Set environment variables in hosting platform
4. Update `BACKEND_API_BASE_URL` to production backend URL

## Troubleshooting

### "Cannot connect to backend"

- Ensure backend is running on port 8000
- Check `BACKEND_API_BASE_URL` in `web/.env`
- Verify API key matches in both `.env` files

### "Database schema out of date"

```bash
cd backend
alembic upgrade head
```

### CORS errors

- Ensure `ALLOWED_ORIGINS` in `backend/.env` includes your frontend URL
- Use Next.js API proxy (recommended) to avoid CORS entirely

## License

This project is provided as-is for MVP purposes.
