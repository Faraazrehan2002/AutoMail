#!/usr/bin/env python3
"""
Test script for API key authentication.
Tests the X-APP-KEY header functionality.

This is NOT a pytest test file - it's a standalone script.
"""

import requests
import os
import sys

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_API_KEY = "some-long-random-string"

def check_endpoint(endpoint, api_key=None, description=""):
    """Check an endpoint with optional API key"""
    headers = {}
    if api_key:
        headers["X-APP-KEY"] = api_key
    
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Endpoint: {endpoint}")
    print(f"API Key: {'Provided' if api_key else 'Not provided'}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(endpoint, headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return response.status_code, response.text
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Server is not running")
        print("   Start the server with: uvicorn app.main:app --reload")
        return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def main():
    print("="*60)
    print("API Key Authentication Test")
    print("="*60)
    
    # Test 1: Health endpoint (should work without API key)
    print("\n📋 Test 1: Health endpoint (no auth required)")
    status, _ = check_endpoint(
        f"{API_BASE_URL}/health",
        description="GET /health (no auth required)"
    )
    
    if status is None:
        print("\n⚠️  Server is not running. Please start it first:")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Test 2: Protected endpoint without API key
    print("\n📋 Test 2: Protected endpoint WITHOUT API key")
    status, response_text = check_endpoint(
        f"{API_BASE_URL}/jobs/test-job-id",
        description="GET /jobs/{job_id} (should require auth)"
    )
    
    if status == 401:
        print("✅ Correctly rejected: 401 Unauthorized")
    elif status == 404:
        print("✅ Endpoint accessible (API key not configured or not required)")
        print("   Note: If APP_API_KEY is not set in .env, API is open")
    else:
        print(f"⚠️  Unexpected status: {status}")
    
    # Test 3: Protected endpoint with WRONG API key
    print("\n📋 Test 3: Protected endpoint with WRONG API key")
    status, response_text = check_endpoint(
        f"{API_BASE_URL}/jobs/test-job-id",
        api_key="wrong-key-12345",
        description="GET /jobs/{job_id} with wrong API key"
    )
    
    if status == 401:
        print("✅ Correctly rejected: 401 Unauthorized (wrong key)")
    elif status == 404:
        print("✅ Endpoint accessible (API key not configured)")
    else:
        print(f"⚠️  Unexpected status: {status}")
    
    # Test 4: Protected endpoint with CORRECT API key
    print("\n📋 Test 4: Protected endpoint with CORRECT API key")
    print(f"   Using test API key: {TEST_API_KEY}")
    print("   Note: This will only work if APP_API_KEY matches in .env")
    
    status, response_text = check_endpoint(
        f"{API_BASE_URL}/jobs/test-job-id",
        api_key=TEST_API_KEY,
        description="GET /jobs/{job_id} with correct API key"
    )
    
    if status == 200 or status == 404:
        print("✅ Request accepted (404 is expected for non-existent job)")
    elif status == 401:
        print("⚠️  Rejected: API key doesn't match")
        print("   Set APP_API_KEY=some-long-random-string in .env to test")
    else:
        print(f"⚠️  Unexpected status: {status}")
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("To enable API key authentication:")
    print("1. Add to .env: APP_API_KEY=some-long-random-string")
    print("2. Restart the server")
    print("3. Use header: X-APP-KEY: some-long-random-string")
    print("\nTo test with curl:")
    print(f'  curl -H "X-APP-KEY: {TEST_API_KEY}" {API_BASE_URL}/jobs/test-id')

if __name__ == "__main__":
    main()
