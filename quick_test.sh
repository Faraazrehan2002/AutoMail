#!/bin/bash
# Quick test with the API key from .env

API_BASE="http://localhost:8000"
API_KEY="some-long-random-string"

echo "Testing API Key: $API_KEY"
echo ""

echo "1. Health (no auth):"
curl -s http://localhost:8000/health | head -3
echo -e "\n"

echo "2. Jobs endpoint WITHOUT key (should fail if APP_API_KEY set):"
curl -s -w "\nStatus: %{http_code}\n" http://localhost:8000/jobs/test-id
echo ""

echo "3. Jobs endpoint WITH key:"
curl -s -w "\nStatus: %{http_code}\n" -H "X-APP-KEY: $API_KEY" http://localhost:8000/jobs/test-id
echo ""

echo "4. Jobs endpoint with WRONG key:"
curl -s -w "\nStatus: %{http_code}\n" -H "X-APP-KEY: wrong-key" http://localhost:8000/jobs/test-id
echo ""
