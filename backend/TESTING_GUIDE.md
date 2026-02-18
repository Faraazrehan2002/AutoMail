# Backend Testing Guide

## Quick Test Commands

### 1. Test Health Endpoint
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"OK","timestamp":"..."}`

### 2. Test User Registration
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```
Expected: JSON with `access_token`, `refresh_token`, and `user` object

### 3. Test User Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```
Expected: JSON with tokens

### 4. Test List Jobs (with token)
```bash
# Replace YOUR_TOKEN with the access_token from login
curl http://localhost:8000/jobs \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Expected: List of jobs (may be empty)

### 5. Test Create Template
```bash
curl -X POST http://localhost:8000/templates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Welcome Email",
    "subject": "Welcome {{name}}!",
    "html_body": "<p>Hello {{name}}, welcome to {{company}}!</p>"
  }'
```
Expected: Created template object

### 6. Test List Templates
```bash
curl http://localhost:8000/templates \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Expected: List of templates

### 7. Test Analytics Overview
```bash
curl "http://localhost:8000/analytics/overview?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Expected: Analytics data with daily metrics

### 8. Test Batch Progress (404 expected for non-existent batch)
```bash
curl "http://localhost:8000/jobs/test-job/batches/test-batch/progress" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Expected: `404` status with error message

## Using the Test Script

Run the automated test script:
```bash
cd backend
python test_backend.py
```

Make sure the backend is running first:
```bash
uvicorn app.main:app --reload
```

## Testing with Postman/Insomnia

1. **Import Collection**: Create requests for all endpoints
2. **Set Base URL**: `http://localhost:8000`
3. **Auth Flow**:
   - Register → Get token
   - Use token in Authorization header: `Bearer <token>`
4. **Test Endpoints**:
   - `/auth/register`
   - `/auth/login`
   - `/auth/refresh`
   - `/jobs` (with auth)
   - `/templates` (with auth)
   - `/analytics/overview` (with auth)

## Expected Results

✅ **All endpoints should return proper status codes:**
- `200` for successful GET/POST
- `201` for successful creation
- `404` for not found
- `401` for unauthorized (without token)
- `403` for forbidden (wrong user)

✅ **Authentication should work:**
- Register creates user
- Login returns tokens
- Protected routes require token
- Refresh token works

✅ **Templates should work:**
- Create, read, update, delete
- Variables extracted correctly

✅ **Analytics should work:**
- Returns overview data
- Handles date ranges

## Common Issues

**401 Unauthorized:**
- Missing or invalid token
- Token expired (use refresh endpoint)

**404 Not Found:**
- Resource doesn't exist (expected for test IDs)
- Wrong endpoint URL

**500 Internal Server Error:**
- Check backend logs
- Database migration may be needed: `alembic upgrade head`
