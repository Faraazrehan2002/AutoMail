#!/bin/bash
# Test script for API key authentication

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

# Try to read API key from .env file
if [ -f .env ]; then
    ENV_API_KEY=$(grep "^APP_API_KEY=" .env 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    if [ -n "$ENV_API_KEY" ]; then
        API_KEY="${API_KEY:-$ENV_API_KEY}"
        echo "✓ Found APP_API_KEY in .env file"
    else
        API_KEY="${API_KEY:-some-long-random-string}"
        echo "⚠ APP_API_KEY not found in .env, using default test key"
    fi
else
    API_KEY="${API_KEY:-some-long-random-string}"
    echo "⚠ .env file not found, using default test key"
fi

echo "=========================================="
echo "API Key Authentication Test"
echo "=========================================="
echo "API Base URL: $API_BASE_URL"
echo "Test API Key: $API_KEY"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health endpoint (should work without API key)
echo "Test 1: Health endpoint (no auth required)"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$API_BASE_URL/health")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Status: $HTTP_CODE"
    echo "Response: $BODY"
else
    echo -e "${RED}✗ FAIL${NC} - Status: $HTTP_CODE"
    if [ "$HTTP_CODE" = "000" ]; then
        echo -e "${YELLOW}Server is not running. Start it with:${NC}"
        echo "  uvicorn app.main:app --reload"
        exit 1
    fi
fi
echo ""

# Test 2: Protected endpoint WITHOUT API key
echo "Test 2: Protected endpoint WITHOUT API key"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$API_BASE_URL/jobs/test-job-id")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "401" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Correctly rejected: 401 Unauthorized"
    echo "Response: $BODY"
elif [ "$HTTP_CODE" = "404" ]; then
    echo -e "${YELLOW}⚠ WARNING${NC} - Status: 404 (API key not configured or endpoint reached)"
    echo "This means either:"
    echo "  1. APP_API_KEY is not set in .env (API is open)"
    echo "  2. API key middleware is not working correctly"
else
    echo -e "${RED}✗ FAIL${NC} - Unexpected status: $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

# Test 3: Protected endpoint with WRONG API key
echo "Test 3: Protected endpoint with WRONG API key"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -H "X-APP-KEY: wrong-key-12345" \
    "$API_BASE_URL/jobs/test-job-id")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "401" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Correctly rejected: 401 Unauthorized (wrong key)"
    echo "Response: $BODY"
elif [ "$HTTP_CODE" = "404" ]; then
    echo -e "${YELLOW}⚠ WARNING${NC} - Status: 404 (API key not configured)"
else
    echo -e "${RED}✗ FAIL${NC} - Unexpected status: $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

# Test 4: Protected endpoint with CORRECT API key
echo "Test 4: Protected endpoint with CORRECT API key"
echo "----------------------------------------"
echo "Using API key from environment or default: $API_KEY"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -H "X-APP-KEY: $API_KEY" \
    "$API_BASE_URL/jobs/test-job-id")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "404" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Request accepted (404 is expected for non-existent job)"
    echo "Response: $BODY"
elif [ "$HTTP_CODE" = "401" ]; then
    echo -e "${RED}✗ FAIL${NC} - Rejected: API key doesn't match"
    echo "Make sure APP_API_KEY in .env matches the key you're using"
    echo "Current test key: $API_KEY"
    echo "Response: $BODY"
else
    echo -e "${YELLOW}⚠ WARNING${NC} - Unexpected status: $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "To test with your actual API key:"
echo "  export API_KEY=your_actual_api_key_from_env"
echo "  bash test_api_key.sh"
echo ""
echo "Or test manually with curl:"
echo "  curl -H \"X-APP-KEY: your-key\" $API_BASE_URL/jobs/test-id"
echo ""
