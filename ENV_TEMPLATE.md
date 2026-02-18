# Environment Variables Template

Use this template to set up your environment variables for deployment.

## Generate Secret Keys

Run these commands in your terminal to generate secure random keys:

```bash
# Generate APP_API_KEY (32 characters)
openssl rand -hex 32

# Generate JWT_SECRET_KEY (32 characters)
openssl rand -hex 32
```

Or use Python:
```python
import secrets
print("APP_API_KEY:", secrets.token_urlsafe(32))
print("JWT_SECRET_KEY:", secrets.token_urlsafe(32))
```

---

## Backend Environment Variables (Railway/Render)

### Required Variables

```env
# Database (auto-provided by PostgreSQL service)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis (auto-provided by Redis service)
REDIS_URL=redis://host:6379/0

# SendGrid Configuration
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=your-verified-email@yourdomain.com

# Security Keys (generate using commands above)
APP_API_KEY=your_generated_secret_key_here
JWT_SECRET_KEY=your_generated_secret_key_here

# CORS (update after frontend deployment)
ALLOWED_ORIGINS=https://your-app.vercel.app
```

### Optional Variables

```env
# Rate Limiting
EMAILS_PER_SECOND=1.0

# Storage
STORAGE_DIR=./storage

# Max Recipients
MAX_RECIPIENTS_PER_REQUEST=200
```

---

## Frontend Environment Variables (Vercel)

### Required Variables

```env
# Backend API URL (from Railway/Render)
BACKEND_API_BASE_URL=https://your-backend.railway.app

# API Key (must match backend APP_API_KEY)
APP_API_KEY=your_generated_secret_key_here

# App Name (optional)
NEXT_PUBLIC_APP_NAME=AutoMail
```

### Important Notes

- **Never** use `NEXT_PUBLIC_` prefix for secrets
- `BACKEND_API_BASE_URL` should NOT have trailing slash
- `APP_API_KEY` must match exactly between frontend and backend

---

## Example Values

### Development (Local)

**Backend (.env):**
```env
DATABASE_URL=sqlite:///./automail.db
REDIS_URL=redis://localhost:6379/0
SENDGRID_API_KEY=SG.your_dev_key
FROM_EMAIL=dev@example.com
APP_API_KEY=dev_secret_key_12345
JWT_SECRET_KEY=dev_jwt_secret_12345
ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend (web/.env):**
```env
BACKEND_API_BASE_URL=http://localhost:8000
APP_API_KEY=dev_secret_key_12345
NEXT_PUBLIC_APP_NAME=AutoMail
```

### Production

**Backend (Railway/Render):**
```env
DATABASE_URL=postgresql://automail:pass@db.railway.app:5432/railway
REDIS_URL=redis://default:pass@redis.railway.app:6379
SENDGRID_API_KEY=SG.production_key_here
FROM_EMAIL=mail@yourdomain.com
APP_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
JWT_SECRET_KEY=z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k
ALLOWED_ORIGINS=https://your-app.vercel.app
```

**Frontend (Vercel):**
```env
BACKEND_API_BASE_URL=https://your-backend.railway.app
APP_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
NEXT_PUBLIC_APP_NAME=AutoMail
```

---

## Verification Checklist

After setting environment variables:

- [ ] All required variables are set
- [ ] `APP_API_KEY` matches between frontend and backend
- [ ] `ALLOWED_ORIGINS` includes your frontend URL
- [ ] `BACKEND_API_BASE_URL` has no trailing slash
- [ ] `FROM_EMAIL` is verified in SendGrid
- [ ] `SENDGRID_API_KEY` is valid and active
- [ ] Secret keys are strong (32+ characters)
- [ ] No secrets are committed to git

---

## Security Best Practices

1. **Never commit `.env` files to git**
2. **Use different keys for development and production**
3. **Rotate keys periodically**
4. **Use strong, random keys (32+ characters)**
5. **Limit `ALLOWED_ORIGINS` to specific domains**
6. **Keep secrets in secure password manager**
7. **Use environment variable management tools**

---

## Troubleshooting

### "Invalid API Key" errors
- Verify `APP_API_KEY` matches exactly in frontend and backend
- Check for extra spaces or newlines
- Ensure no quotes around values

### CORS errors
- Verify `ALLOWED_ORIGINS` includes exact frontend URL
- Check for protocol mismatch (http vs https)
- Ensure no trailing slashes

### Database connection errors
- Verify `DATABASE_URL` format is correct
- Check database service is running
- Verify credentials are correct

### Redis connection errors
- Verify `REDIS_URL` format is correct
- Check Redis service is running
- Verify credentials are correct
