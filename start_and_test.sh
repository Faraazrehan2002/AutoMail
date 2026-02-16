#!/bin/bash
# Start server and run API key tests

set -e

API_BASE="http://localhost:8000"
API_KEY="${API_KEY:-some-long-random-string}"

echo "=========================================="
echo "Starting AutoMail Server and Running Tests"
echo "=========================================="
echo ""

# Check if server is already running
if curl -s "$API_BASE/health" > /dev/null 2>&1; then
    echo "✓ Server is already running"
else
    echo "Starting server in background..."
    cd "$(dirname "$0")"
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
    SERVER_PID=$!
    echo "Server PID: $SERVER_PID"
    
    # Wait for server to start
    echo "Waiting for server to start..."
    for i in {1..10}; do
        if curl -s "$API_BASE/health" > /dev/null 2>&1; then
            echo "✓ Server started successfully"
            break
        fi
        sleep 1
        echo "  Attempt $i/10..."
    done
    
    if ! curl -s "$API_BASE/health" > /dev/null 2>&1; then
        echo "✗ Server failed to start. Check server.log for errors"
        cat server.log
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Running API Key Tests"
echo "=========================================="
echo ""

# Test 1: Health endpoint
echo "Test 1: Health endpoint (no auth required)"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$API_BASE/health")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ PASS - Status: $HTTP_CODE"
    echo "Response: $BODY"
else
    echo "✗ FAIL - Status: $HTTP_CODE"
fi
echo ""

# Test 2: Protected endpoint without API key
echo "Test 2: Protected endpoint WITHOUT API key"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$API_BASE/jobs/test-job-id")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')
if [ "$HTTP_CODE" = "401" ]; then
    echo "✓ PASS - Correctly rejected: 401 Unauthorized"
    echo "Response: $BODY"
elif [ "$HTTP_CODE" = "404" ]; then
    echo "⚠ WARNING - Status: 404 (API key may not be configured)"
    echo "Response: $BODY"
else
    echo "✗ FAIL - Unexpected status: $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

# Test 3: Protected endpoint with WRONG API key
echo "Test 3: Protected endpoint with WRONG API key"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -H "X-APP-KEY: wrong-key-12345" \
    "$API_BASE/jobs/test-job-id")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')
if [ "$HTTP_CODE" = "401" ]; then
    echo "✓ PASS - Correctly rejected: 401 Unauthorized (wrong key)"
    echo "Response: $BODY"
elif [ "$HTTP_CODE" = "404" ]; then
    echo "⚠ WARNING - Status: 404 (API key may not be configured)"
else
    echo "✗ FAIL - Unexpected status: $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

# Test 4: Protected endpoint with CORRECT API key
echo "Test 4: Protected endpoint with CORRECT API key"
echo "----------------------------------------"
echo "Using API key: $API_KEY"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -H "X-APP-KEY: $API_KEY" \
    "$API_BASE/jobs/test-job-id")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')
if [ "$HTTP_CODE" = "404" ]; then
    echo "✓ PASS - Request accepted (404 is expected for non-existent job)"
    echo "Response: $BODY"
elif [ "$HTTP_CODE" = "401" ]; then
    echo "✗ FAIL - Rejected: API key doesn't match"
    echo "Make sure APP_API_KEY in .env matches: $API_KEY"
    echo "Response: $BODY"
else
    echo "⚠ WARNING - Unexpected status: $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "To stop the server, run:"
echo "  pkill -f 'uvicorn app.main:app'"
echo ""
echo "Or if you know the PID:"
echo "  kill $SERVER_PID"
echo ""
