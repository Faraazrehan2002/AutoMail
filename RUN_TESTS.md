# Running API Key Tests

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure `.env` file has `APP_API_KEY` set:**
   ```bash
   # In .env file
   APP_API_KEY=some-long-random-string
   ```

## Start the Server

```bash
uvicorn app.main:app --reload
```

The server will start on `http://localhost:8000`

## Run Tests

### Option 1: Automated Test Script

```bash
bash test_api_key.sh
```

Or with your actual API key:
```bash
API_KEY="your-actual-key-from-env" bash test_api_key.sh
```

### Option 2: Manual curl Tests

**1. Test health endpoint (no auth required):**
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"OK","timestamp":"..."}`

**2. Test protected endpoint WITHOUT API key:**
```bash
curl http://localhost:8000/jobs/test-job-id
```
Expected: `{"detail":"Unauthorized: Invalid or missing API key"}` with status 401

**3. Test protected endpoint with WRONG API key:**
```bash
curl -H "X-APP-KEY: wrong-key-12345" \
  http://localhost:8000/jobs/test-job-id
```
Expected: `{"detail":"Unauthorized: Invalid or missing API key"}` with status 401

**4. Test protected endpoint with CORRECT API key:**
```bash
curl -H "X-APP-KEY: some-long-random-string" \
  http://localhost:8000/jobs/test-job-id
```
Expected: `{"detail":"Job not found"}` with status 404 (auth passed, job doesn't exist)

**5. Test upload endpoint with API key:**
```bash
curl -X POST \
  -H "X-APP-KEY: some-long-random-string" \
  -F "file=@example.pdf" \
  http://localhost:8000/upload
```

## Expected Results

If `APP_API_KEY` is set in `.env`:
- ✅ Health endpoint works without key
- ✅ Protected endpoints return 401 without key
- ✅ Protected endpoints return 401 with wrong key
- ✅ Protected endpoints accept requests with correct key

If `APP_API_KEY` is NOT set:
- ✅ All endpoints are accessible (API is open)
- ⚠️ This is for development only - set API key for production

## Quick Test Command

```bash
# Set your API key
export API_KEY="some-long-random-string"

# Run all tests
bash start_and_test.sh
```
