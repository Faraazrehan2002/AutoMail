#!/bin/bash
# Test script that uses the actual API key from .env

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

# Get API key from .env
if [ -f .env ]; then
    # Try to extract APP_API_KEY (handle various formats)
    ENV_KEY=$(grep -E "^APP_API_KEY" .env 2>/dev/null | sed 's/^[^=]*=//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | tr -d '"' | tr -d "'" | head -1)
    
    if [ -n "$ENV_KEY" ] && [ "$ENV_KEY" != "" ]; then
        API_KEY="$ENV_KEY"
        echo "✓ Using API key from .env: ${API_KEY:0:10}..."
    else
        echo "✗ Could not find APP_API_KEY in .env"
        echo "Please set it manually: export API_KEY=your-key"
        exit 1
    fi
else
    echo "✗ .env file not found"
    exit 1
fi

echo ""
echo "=========================================="
echo "API Key Authentication Test"
echo "=========================================="
echo "API Base URL: $API_BASE_URL"
echo "Using API key from .env"
echo ""

# Test 1: Health endpoint
echo "Test 1: Health endpoint (no auth required)"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$API_BASE_URL/health")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ PASS - Status: $HTTP_CODE"
else
    echo "✗ FAIL - Status: $HTTP_CODE"
fi
echo ""

# Test 2: Without API key
echo "Test 2: Protected endpoint WITHOUT API key"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$API_BASE_URL/jobs/test-job-id")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')
if [ "$HTTP_CODE" = "401" ]; then
    echo "✓ PASS - Correctly rejected: 401 Unauthorized"
elif [ "$HTTP_CODE" = "404" ]; then
    echo "⚠ WARNING - Status: 404 (API key may not be configured)"
else
    echo "✗ FAIL - Unexpected status: $HTTP_CODE"
fi
echo ""

# Test 3: With WRONG API key
echo "Test 3: Protected endpoint with WRONG API key"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -H "X-APP-KEY: wrong-key-12345" \
    "$API_BASE_URL/jobs/test-job-id")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')
if [ "$HTTP_CODE" = "401" ]; then
    echo "✓ PASS - Correctly rejected: 401 Unauthorized (wrong key)"
elif [ "$HTTP_CODE" = "404" ]; then
    echo "⚠ WARNING - Status: 404 (API key may not be configured)"
else
    echo "✗ FAIL - Unexpected status: $HTTP_CODE"
fi
echo ""

# Test 4: With CORRECT API key
echo "Test 4: Protected endpoint with CORRECT API key"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -H "X-APP-KEY: $API_KEY" \
    "$API_BASE_URL/jobs/test-job-id")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')
if [ "$HTTP_CODE" = "404" ]; then
    echo "✓ PASS - Request accepted (404 is expected for non-existent job)"
    echo "Response: $BODY"
elif [ "$HTTP_CODE" = "401" ]; then
    echo "✗ FAIL - Rejected: API key doesn't match"
    echo "Response: $BODY"
    echo ""
    echo "Debug info:"
    echo "  API key from .env: ${API_KEY:0:20}..."
    echo "  Check that APP_API_KEY in .env matches what the server loaded"
else
    echo "⚠ WARNING - Unexpected status: $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

echo "=========================================="
echo "Test Complete"
echo "=========================================="
