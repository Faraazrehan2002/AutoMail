# Create backend/.env File

The backend server needs a `.env` file. Create it with this content:

```bash
cd backend
cat > .env << 'EOF'
# SendGrid Configuration (required for sending emails)
# Get your API key from https://app.sendgrid.com/settings/api_keys
SENDGRID_API_KEY=
FROM_EMAIL=

# Database
DATABASE_URL=sqlite:///./automail.db

# Rate Limiting
EMAILS_PER_SECOND=1.0

# Security (required for API access)
APP_API_KEY=some-long-random-string-change-this

# CORS (comma-separated origins, or "*" for all)
ALLOWED_ORIGINS=http://localhost:3000

# Development
AUTO_MIGRATE_DEV=false
EOF
```

**Important:**
- Fill in `SENDGRID_API_KEY` and `FROM_EMAIL` if you want to send real emails
- The server will start without them, but email sending will fail
- Use the same `APP_API_KEY` value in `web/.env` as well

## Quick Start (Without SendGrid)

If you just want to test the app without sending emails:

```bash
cd backend
cat > .env << 'EOF'
SENDGRID_API_KEY=
FROM_EMAIL=
DATABASE_URL=sqlite:///./automail.db
EMAILS_PER_SECOND=1.0
APP_API_KEY=test-key-123
ALLOWED_ORIGINS=http://localhost:3000
AUTO_MIGRATE_DEV=false
EOF
```

The server will start, but email sending will show errors (which is fine for testing the UI).
