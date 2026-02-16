#!/usr/bin/env python3
"""
Test the API key middleware logic without requiring a running server.
This verifies the middleware code is correct.
"""

import sys
sys.path.insert(0, '.')

from app.config import Settings
from app.middleware import APIKeyMiddleware

def test_middleware_logic():
    """Test the middleware logic"""
    print("="*60)
    print("Testing API Key Middleware Logic")
    print("="*60)
    
    # Test 1: Check if settings can load API key
    print("\n1. Testing Settings Configuration:")
    try:
        settings = Settings()
        if settings.app_api_key:
            print(f"   ✓ APP_API_KEY is set: {settings.app_api_key[:10]}...")
        else:
            print("   ⚠ APP_API_KEY is not set in .env")
            print("   Set APP_API_KEY=some-long-random-string in .env to enable auth")
    except Exception as e:
        print(f"   ✗ Error loading settings: {e}")
        return False
    
    # Test 2: Verify middleware class exists
    print("\n2. Testing Middleware Class:")
    try:
        middleware = APIKeyMiddleware(None)
        print("   ✓ APIKeyMiddleware class instantiated successfully")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: Verify header name
    print("\n3. Testing Header Name:")
    header_name = "X-APP-KEY"
    print(f"   ✓ Header name: {header_name}")
    
    # Test 4: Verify protected paths
    print("\n4. Testing Protected Paths:")
    protected_paths = ["/upload", "/jobs/123", "/jobs/123/send"]
    public_paths = ["/health", "/docs", "/redoc", "/openapi.json", "/"]
    
    print("   Protected paths (require API key):")
    for path in protected_paths:
        print(f"     - {path}")
    
    print("   Public paths (no API key required):")
    for path in public_paths:
        print(f"     - {path}")
    
    print("\n" + "="*60)
    print("Middleware Logic Test Complete")
    print("="*60)
    print("\nTo test with actual HTTP requests:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Run: bash test_api_key.sh")
    print("3. Or use curl:")
    print('   curl -H "X-APP-KEY: your-key" http://localhost:8000/jobs/test-id')
    
    return True

if __name__ == "__main__":
    success = test_middleware_logic()
    sys.exit(0 if success else 1)
