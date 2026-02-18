# AutoMail Deployment Guide

Complete guide for deploying AutoMail to production.

## Architecture

- **Backend**: FastAPI (Python) - REST API + WebSocket
- **Frontend**: Next.js 14+ (TypeScript) - Web UI
- **Database**: PostgreSQL (production) or SQLite (development)
- **Queue**: Redis + RQ for background jobs
- **Worker**: RQ worker for processing email sends
- **Scheduler**: Background process for scheduled sends

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional, for Redis/Postgres)
- SendGrid API key

### Quick Start

1. **Clone and setup backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your SendGrid credentials
   ```

2. **Setup database:**
   ```bash
   alembic upgrade head
   ```

3. **Start Redis (Docker):**
   ```bash
   docker-compose up -d redis
   ```

4. **Start services:**
   ```bash
   # Terminal 1: Backend API
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2: Worker
   cd backend
   python worker.py

   # Terminal 3: Scheduler (optional)
   cd backend
   python scheduler.py

   # Terminal 4: Frontend
   cd web
   npm install
   npm run dev
   ```

### Using Docker Compose (Full Stack)

```bash
# Copy environment file
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Production Deployment

### Option 1: Vercel (Frontend) + Render/Railway (Backend)

#### Frontend (Vercel)

1. **Connect GitHub repository to Vercel**
2. **Set root directory to `web/`**
3. **Environment variables:**
   ```
   BACKEND_API_BASE_URL=https://your-backend.railway.app
   APP_API_KEY=your_secret_key
   NEXT_PUBLIC_API_BASE=/api
   ```
4. **Deploy**

#### Backend (Render/Railway/Fly.io)

**Render Setup:**

1. **Create new Web Service**
2. **Build command:** `cd backend && pip install -r requirements.txt && alembic upgrade head`
3. **Start command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment variables:**
   ```
   DATABASE_URL=postgresql://... (provided by Render)
   REDIS_URL=redis://... (use Render Redis addon)
   SENDGRID_API_KEY=your_key
   FROM_EMAIL=mail@yourdomain.com
   APP_API_KEY=your_secret_key
   JWT_SECRET_KEY=generate_secure_random_string
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```
5. **Add Background Worker:**
   - Build: `cd backend && pip install -r requirements.txt`
   - Start: `cd backend && python worker.py`
   - Same environment variables

6. **Add Scheduler (optional):**
   - Build: `cd backend && pip install -r requirements.txt`
   - Start: `cd backend && python scheduler.py`

**Railway Setup:**

1. **Create new project**
2. **Add PostgreSQL service**
3. **Add Redis service**
4. **Deploy backend:**
   - Root: `backend/`
   - Build: `pip install -r requirements.txt && alembic upgrade head`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Deploy worker:**
   - Same repo, different service
   - Start: `python worker.py`
6. **Deploy scheduler:**
   - Same repo, different service
   - Start: `python scheduler.py`

### Option 2: Docker Compose (VPS)

1. **Setup server (Ubuntu/Debian):**
   ```bash
   # Install Docker & Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

2. **Clone repository:**
   ```bash
   git clone <your-repo>
   cd AutoMail
   ```

3. **Configure environment:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with production values
   ```

4. **Update docker-compose.yml:**
   - Change `DATABASE_URL` to production Postgres
   - Set strong `JWT_SECRET_KEY`
   - Set `ALLOWED_ORIGINS` to your domain
   - Remove port mappings for production (use reverse proxy)

5. **Start services:**
   ```bash
   docker-compose up -d
   ```

6. **Setup reverse proxy (Nginx):**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }

       location /ws {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

7. **SSL with Let's Encrypt:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
# Or for SQLite (dev): sqlite:///./automail.db

# Redis
REDIS_URL=redis://localhost:6379/0

# SendGrid
SENDGRID_API_KEY=your_api_key
FROM_EMAIL=mail@yourdomain.com

# Security
APP_API_KEY=your_secret_api_key
JWT_SECRET_KEY=generate_secure_random_string_here

# CORS
ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Rate Limiting
EMAILS_PER_SECOND=1.0

# Storage
STORAGE_DIR=./storage
```

### Frontend (web/.env)

```env
BACKEND_API_BASE_URL=https://your-backend.railway.app
APP_API_KEY=your_secret_key
NEXT_PUBLIC_API_BASE=/api
```

## Database Migrations

**Local:**
```bash
cd backend
alembic upgrade head
```

**Production:**
```bash
# On Render/Railway, migrations run automatically during build
# Or manually:
alembic upgrade head
```

## Monitoring

### Health Checks

- Backend: `GET /health`
- Worker: Check logs for processing messages
- Scheduler: Check logs for scheduled batch processing

### Logs

**Docker Compose:**
```bash
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f scheduler
```

**Render/Railway:**
- View logs in dashboard
- Set up log aggregation if needed

## Scaling

### Horizontal Scaling

- **Backend**: Can run multiple instances (stateless)
- **Worker**: Run multiple workers for parallel processing
- **Scheduler**: Only one instance needed
- **Redis**: Single instance (or Redis Cluster for high scale)
- **PostgreSQL**: Single instance (or read replicas)

### Vertical Scaling

- Increase worker instances for higher email throughput
- Increase Redis memory for larger queues
- Increase PostgreSQL resources for larger datasets

## Security Checklist

- [ ] Use strong `JWT_SECRET_KEY` (32+ random characters)
- [ ] Use strong `APP_API_KEY` for API authentication
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set `ALLOWED_ORIGINS` to specific domains (not `*`)
- [ ] Use PostgreSQL in production (not SQLite)
- [ ] Keep dependencies updated
- [ ] Use environment variables (never commit secrets)
- [ ] Enable SendGrid domain authentication
- [ ] Set up rate limiting if needed
- [ ] Monitor for suspicious activity

## Troubleshooting

### Worker not processing jobs

1. Check Redis connection: `redis-cli ping`
2. Check worker logs for errors
3. Verify queue name matches: `emails`
4. Check database connection

### WebSocket not connecting

1. Verify Redis is running (for pub/sub)
2. Check CORS settings
3. Verify WebSocket endpoint: `WS /ws/jobs/{job_id}/batches/{batch_id}`
4. Check browser console for errors

### Scheduled emails not sending

1. Verify scheduler process is running
2. Check scheduler logs
3. Verify `scheduled_for` is in the future
4. Check batch status in database

### Database connection issues

1. Verify `DATABASE_URL` is correct
2. Check database is accessible
3. Run migrations: `alembic upgrade head`
4. Check connection pool settings

## Backup & Recovery

### Database Backup

**PostgreSQL:**
```bash
pg_dump -U automail automail > backup.sql
```

**Restore:**
```bash
psql -U automail automail < backup.sql
```

### Automated Backups

Set up cron job or use managed database backup service.

## Support

For issues or questions:
1. Check logs first
2. Review this deployment guide
3. Check GitHub issues
4. Review application logs
