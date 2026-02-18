#!/bin/bash
# Quick backend test script

BASE_URL="http://localhost:8000"

echo "🧪 Testing AutoMail Backend"
echo "============================"
echo ""

# Test 1: Health
echo "1. Testing Health Endpoint..."
HEALTH=$(curl -s "$BASE_URL/health")
if echo "$HEALTH" | grep -q "OK"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# Test 2: Register
echo ""
echo "2. Testing User Registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test'$(date +%s)'@test.com",
    "password": "testpass123",
    "full_name": "Test User"
  }')

if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
    echo "✅ Registration passed"
    TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "   Token: ${TOKEN:0:20}..."
else
    echo "❌ Registration failed"
    echo "   Response: $REGISTER_RESPONSE"
    exit 1
fi

# Test 3: List Jobs
echo ""
echo "3. Testing List Jobs (with auth)..."
JOBS_RESPONSE=$(curl -s "$BASE_URL/jobs?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN")

if echo "$JOBS_RESPONSE" | grep -q "jobs"; then
    echo "✅ List jobs passed"
else
    echo "⚠️  List jobs returned: $JOBS_RESPONSE"
fi

# Test 4: Create Template
echo ""
echo "4. Testing Create Template..."
TEMPLATE_RESPONSE=$(curl -s -X POST "$BASE_URL/templates" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Template",
    "subject": "Hello {{name}}",
    "html_body": "<p>Hello {{name}}!</p>"
  }')

if echo "$TEMPLATE_RESPONSE" | grep -q "id"; then
    echo "✅ Create template passed"
    TEMPLATE_ID=$(echo "$TEMPLATE_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
else
    echo "❌ Create template failed"
    echo "   Response: $TEMPLATE_RESPONSE"
fi

# Test 5: List Templates
echo ""
echo "5. Testing List Templates..."
TEMPLATES_RESPONSE=$(curl -s "$BASE_URL/templates" \
  -H "Authorization: Bearer $TOKEN")

if echo "$TEMPLATES_RESPONSE" | grep -q "\["; then
    echo "✅ List templates passed"
else
    echo "⚠️  List templates returned: $TEMPLATES_RESPONSE"
fi

# Test 6: Analytics
echo ""
echo "6. Testing Analytics Overview..."
ANALYTICS_RESPONSE=$(curl -s "$BASE_URL/analytics/overview?days=30" \
  -H "Authorization: Bearer $TOKEN")

if echo "$ANALYTICS_RESPONSE" | grep -q "total_jobs"; then
    echo "✅ Analytics passed"
else
    echo "⚠️  Analytics returned: $ANALYTICS_RESPONSE"
fi

echo ""
echo "============================"
echo "✅ Basic tests completed!"
echo ""
echo "To test more features:"
echo "  - Upload a PDF: POST /upload"
echo "  - Send emails: POST /jobs/{job_id}/send"
echo "  - Check progress: GET /jobs/{job_id}/batches/{batch_id}/progress"
echo "  - Schedule: POST /jobs/{job_id}/schedule"
