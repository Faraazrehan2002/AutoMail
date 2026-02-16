# API Key Authentication Test Commands

Use these curl commands to test the API key authentication:

## Prerequisites

1. Make sure the server is running:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Set your API key (from .env):
   ```bash
   export API_KEY="your-actual-api-key-from-env"
   ```

## Test Commands

### 1. Health endpoint (no auth required)
```bash
curl http://localhost:8000/health
```
**Expected**: 200 OK

### 2. Protected endpoint WITHOUT API key
```bash
curl http://localhost:8000/jobs/test-job-id
```
**Expected**: 401 Unauthorized (if APP_API_KEY is set in .env)

### 3. Protected endpoint with WRONG API key
```bash
curl -H "X-APP-KEY: wrong-key-12345" \
  http://localhost:8000/jobs/test-job-id
```
**Expected**: 401 Unauthorized

### 4. Protected endpoint with CORRECT API key
```bash
curl -H "X-APP-KEY: some-long-random-string" \
  http://localhost:8000/jobs/test-job-id
```
**Expected**: 404 Not Found (job doesn't exist, but auth passed)

### 5. Upload endpoint with API key
```bash
curl -X POST \
  -H "X-APP-KEY: some-long-random-string" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@example.pdf" \
  http://localhost:8000/upload
```

### 6. Send endpoint with API key
```bash
curl -X POST \
  -H "X-APP-KEY: some-long-random-string" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test",
    "html_body": "<p>Test</p>",
    "recipients": ["test@example.com"],
    "dry_run": true
  }' \
  http://localhost:8000/jobs/{job_id}/send
```

## Quick Test Script

Run the automated test:
```bash
bash test_api_key.sh
```

Or with a specific API key:
```bash
API_KEY="your-key-here" bash test_api_key.sh
```
