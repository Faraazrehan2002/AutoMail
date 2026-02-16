# AutoMail API

A production-ready FastAPI backend MVP for extracting email addresses from PDFs and sending emails via SendGrid with rate limiting.

## Features

- 📄 **PDF Upload & Processing**: Upload PDF files and extract email addresses
- 📧 **Email Extraction**: Robust regex-based extraction with validation and deduplication
- 👤 **Metadata Extraction**: Optional extraction of names and companies associated with emails
- 📨 **SendGrid Integration**: Send emails via SendGrid API with rate limiting
- 📊 **Job Management**: Track PDF processing jobs and email sending status
- 🔒 **Guardrails**: Rate limiting, recipient limits, and validation
- 💾 **SQLite Database**: Persistent storage with SQLAlchemy 2.0 ORM
- 🧪 **Testing**: Basic test suite for email extraction

## Requirements

- Python 3.11+
- SendGrid API key
- Verified sender email address in SendGrid

## Setup

### 1. Clone and Install Dependencies

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```env
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=your_verified_sender@example.com
DATABASE_URL=sqlite:///./automail.db
EMAILS_PER_SECOND=1.0

# Security (optional but recommended)
APP_API_KEY=your_secret_api_key_here

# CORS (comma-separated origins, or "*" for all)
ALLOWED_ORIGINS=*
```

**Important**: 
- Get your SendGrid API key from the [SendGrid Dashboard](https://app.sendgrid.com/settings/api_keys)
- Verify your sender email address in SendGrid before sending emails
- See [SendGrid Sender Verification](https://docs.sendgrid.com/ui/sending-email/sender-verification) for details

### 3. Initialize Database

The database will be automatically initialized on first run, but you should run migrations to ensure the schema is up to date:

```bash
# Apply all pending migrations
alembic upgrade head

# Verify database schema
python scripts/db_check.py
```

**Note**: On startup, the application will warn if migrations are behind. In development, you can set `AUTO_MIGRATE_DEV=true` in `.env` to automatically run migrations on startup (not recommended for production).

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## API Authentication

If `APP_API_KEY` is set in your `.env` file, all endpoints except `/health` and `/docs` require authentication via the `X-APP-KEY` header:

```bash
curl -H "X-APP-KEY: your_secret_api_key_here" http://localhost:8000/upload
```

**Note**: If `APP_API_KEY` is not set, the API is open (useful for development).

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "OK",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Upload PDF

Upload a PDF file to extract email addresses.

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "X-APP-KEY: your_api_key" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@example.pdf"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "example.pdf",
  "file_path": "./storage/550e8400-e29b-41d4-a716-446655440000.pdf",
  "status": "completed",
  "created_at": "2024-01-01T12:00:00",
  "recipient_count": 15
}
```

**Error Responses:**
- `400`: Invalid file type (only PDFs supported)
- `400`: PDF appears scanned (no extractable text)
- `500`: Processing error

### Get Job Details

Retrieve job information and extracted recipients.

```bash
curl -H "X-APP-KEY: your_api_key" \
  "http://localhost:8000/jobs/{job_id}"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "example.pdf",
  "file_path": "./storage/550e8400-e29b-41d4-a716-446655440000.pdf",
  "status": "completed",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": null,
  "recipient_count": 15,
  "recipients": [
    {
      "email": "john.doe@example.com",
      "name": "John Doe",
      "company": "Example"
    },
    {
      "email": "jane.smith@company.com",
      "name": "Jane Smith",
      "company": "Company"
    }
  ]
}
```

**Error Responses:**
- `404`: Job not found

### Send Emails

Send emails to selected recipients from a job. Supports dry-run mode for testing.

```bash
curl -X POST "http://localhost:8000/jobs/{job_id}/send" \
  -H "accept: application/json" \
  -H "X-APP-KEY: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Hello from AutoMail",
    "html_body": "<h1>Hello!</h1><p>This is a test email.</p>",
    "recipients": [
      "john.doe@example.com",
      "jane.smith@company.com"
    ],
    "personalization": {
      "john.doe@example.com": {
        "name": "John",
        "company": "Example Corp"
      }
    },
    "dry_run": false
  }'
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "batch_id": "660e8400-e29b-41d4-a716-446655440001",
  "total_recipients": 2,
  "queued": 2,
  "sent": 2,
  "failed": 0,
  "dry_run": false,
  "results": [
    {
      "email": "john.doe@example.com",
      "status": "sent",
      "error_message": null,
      "sendgrid_message_id": "abc123"
    },
    {
      "email": "jane.smith@company.com",
      "status": "sent",
      "error_message": null,
      "sendgrid_message_id": "def456"
    }
  ]
}
```

**Request Body:**
- `subject` (required): Email subject line
- `html_body` (required): HTML email content
- `recipients` (required): Array of email addresses (max 200)
- `personalization` (optional): Dictionary mapping email addresses to personalization data
- `dry_run` (optional, default: false): If true, validates but doesn't send emails

**Dry Run Mode:**
Set `dry_run: true` to test email sending without actually sending. Useful for validation and testing.

**Error Responses:**
- `400`: Empty subject or body
- `400`: Recipients not found in job
- `400`: Too many recipients (exceeds limit)
- `404`: Job not found

### Get Batch Status

Retrieve the status and results of a specific send batch.

```bash
curl -H "X-APP-KEY: your_api_key" \
  "http://localhost:8000/jobs/{job_id}/batches/{batch_id}"
```

**Response:**
```json
{
  "batch_id": "660e8400-e29b-41d4-a716-446655440001",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_recipients": 2,
  "queued": 0,
  "sent": 2,
  "failed": 0,
  "created_at": "2024-01-01T12:00:00",
  "results": [
    {
      "email": "john.doe@example.com",
      "status": "sent",
      "error_message": null,
      "sendgrid_message_id": "abc123"
    }
  ]
}
```

## Guardrails

- **Max Recipients**: 200 recipients per send request (configurable)
- **Rate Limiting**: 1 email per second by default (configurable via `EMAILS_PER_SECOND`)
- **Validation**: Subject and body must not be empty
- **Recipient Validation**: Only recipients extracted from the PDF can receive emails
- **Email Validation**: All extracted emails are validated using email-validator

## Project Structure

```
AutoMail/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py             # Configuration management
│   ├── db.py                 # Database setup
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── middleware.py         # API key authentication middleware
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── jobs.py           # Job management endpoints
│   │   └── health.py          # Health check endpoint
│   └── services/
│       ├── __init__.py
│       ├── pdf_extract.py    # PDF text extraction (with pypdf fallback)
│       ├── email_extract.py  # Email extraction logic
│       ├── sendgrid_client.py # SendGrid API client
│       └── mailer.py          # Email sending with rate limiting
├── scripts/
│   └── smoke_test.py         # Smoke test script
├── alembic/                  # Database migrations
├── storage/                  # Uploaded PDF files
├── tests/                    # Test suite
│   └── test_email_extract.py
├── .env.example              # Environment variables template
├── alembic.ini               # Alembic configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Database Schema

### Jobs Table
- `id`: Unique job identifier (UUID)
- `filename`: Original PDF filename
- `file_path`: Path to stored PDF file
- `status`: Job status (processing, completed, failed)
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Recipients Table
- `id`: Primary key
- `job_id`: Foreign key to jobs
- `email`: Email address
- `name`: Extracted name (optional)
- `company`: Extracted company (optional)
- `extracted_at`: Timestamp

### Send Logs Table
- `id`: Primary key
- `batch_id`: UUID for batch tracking (indexed, required)
- `job_id`: Foreign key to jobs (indexed)
- `recipient_email`: Recipient email address (indexed)
- `status`: Send status (queued, sent, failed)
- `error_message`: Error message if failed
- `sendgrid_message_id`: SendGrid message ID
- `sent_at`: Timestamp when email was sent
- `created_at`: Timestamp when log entry was created (required)
- `personalization`: JSON personalization data

## Smoke Test

A smoke test script is provided to quickly verify the full workflow:

```bash
# Set API key (if required)
export API_KEY=your_api_key_here

# Run smoke test with a PDF file
python scripts/smoke_test.py path/to/your.pdf

# Or use a test email override
export TEST_TO_EMAIL=test@example.com
python scripts/smoke_test.py path/to/your.pdf
```

The smoke test will:
1. Upload the PDF to `/upload`
2. Fetch job details from `/jobs/{job_id}`
3. Select the first 1-3 extracted emails (or use `TEST_TO_EMAIL` if set)
4. Send a test email via `/jobs/{job_id}/send`
5. Print a summary of results

**Environment Variables:**
- `API_BASE_URL`: Base URL for the API (default: http://localhost:8000)
- `API_KEY`: API key for authentication (required if APP_API_KEY is set)
- `TEST_TO_EMAIL`: Override recipient email (optional)

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with verbose output:

```bash
pytest tests/ -v
```

The test suite includes comprehensive tests for:
- Email validation (valid/invalid formats, TLD length checks)
- Email extraction (punctuation stripping, deduplication, sorting)
- Edge cases (uppercase normalization, special characters, duplicates)

## Error Handling

The API provides clear error messages:

- **400 Bad Request**: Invalid input, missing required fields, validation errors
- **404 Not Found**: Job not found
- **500 Internal Server Error**: Unexpected server errors

All errors return JSON responses with descriptive messages.

## PDF Processing Notes

- **Text-based PDFs**: Fully supported with email extraction
- **Fallback parsing**: If pdfplumber fails, pypdf is used as a fallback
- **Scanned PDFs**: Returns structured error if no text can be extracted

The PDF extraction process:
1. First attempts extraction with `pdfplumber`
2. If minimal text is found, falls back to `pypdf`
3. If still no text, returns structured error:

```json
{
  "detail": "{\"error_code\": \"PDF_SCANNED_NO_TEXT\", \"message\": \"PDF appears to be scanned or contains no extractable text. Please enable OCR or provide a PDF with selectable text.\"}"
}
```

## SendGrid Configuration

### Sender Verification

Before sending emails, you must verify your sender email address in SendGrid:

1. Go to [SendGrid Dashboard](https://app.sendgrid.com)
2. Navigate to **Settings** → **Sender Authentication**
3. Verify your sender email address
4. Use the verified email as `FROM_EMAIL` in your `.env` file

### API Key Setup

1. Go to [SendGrid API Keys](https://app.sendgrid.com/settings/api_keys)
2. Create a new API key with **Mail Send** permissions
3. Copy the API key to your `.env` file as `SENDGRID_API_KEY`

**Security Note**: Never commit your `.env` file to version control. The `.env.example` file is provided as a template.

## Rate Limiting

Email sending is rate-limited to prevent overwhelming SendGrid and maintain good sending practices:

- Default: 1 email per second
- Configurable via `EMAILS_PER_SECOND` environment variable
- Rate limiting is applied automatically during batch sends

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload
```

The `--reload` flag enables auto-reload on code changes.

## Database Migrations

### Running Migrations

**First time setup:**
```bash
# Apply all migrations
alembic upgrade head

# Verify schema
python scripts/db_check.py
```

**After code changes:**
```bash
# Generate new migration (if models changed)
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/

# Apply the migration
alembic upgrade head

# Verify
python scripts/db_check.py
```

**Rollback (if needed):**
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

### Migration Safety Checks

The application includes built-in migration checks:

1. **On Startup**: The app checks if migrations are up to date and warns if behind
2. **Auto-migration (Dev only)**: Set `AUTO_MIGRATE_DEV=true` in `.env` to auto-run migrations on startup (development only)
3. **Manual verification**: Run `python scripts/db_check.py` to verify schema

### Troubleshooting

**"no such column: batch_id" or "no such column: created_at" errors:**

This means migrations haven't been applied. Run:
```bash
alembic upgrade head
python scripts/db_check.py
```

**"Table 'alembic_version' doesn't exist":**

This means Alembic hasn't been initialized. Run:
```bash
alembic upgrade head
```

**SQLite-specific issues:**

- SQLite has limited ALTER TABLE support. The migration handles this by:
  - Adding columns as nullable first
  - Backfilling data
  - Making columns non-nullable
- If you encounter issues, you may need to recreate the database:
  ```bash
  # Backup first!
  cp automail.db automail.db.backup
  
  # Delete and recreate
  rm automail.db
  alembic upgrade head
  ```

**Check current migration status:**
```bash
# See current revision
alembic current

# See available revisions
alembic history

# See what would be applied
alembic upgrade head --sql
```

## Production Considerations

Before deploying to production:

1. **Environment Variables**: Use secure secret management (not `.env` files)
2. **Database**: Consider upgrading from SQLite to PostgreSQL for production
3. **CORS**: Update CORS settings to restrict allowed origins
4. **Rate Limiting**: Adjust `EMAILS_PER_SECOND` based on SendGrid plan limits
5. **File Storage**: Consider cloud storage (S3, etc.) instead of local filesystem
6. **Logging**: Set up proper logging infrastructure
7. **Monitoring**: Add application monitoring and error tracking
8. **Security**: Implement authentication and authorization
9. **Backup**: Set up database backups

## License

This project is provided as-is for MVP purposes.

## Support

For issues or questions, please refer to the FastAPI and SendGrid documentation:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SendGrid Documentation](https://docs.sendgrid.com/)
