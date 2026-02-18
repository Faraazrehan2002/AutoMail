#!/usr/bin/env python3
"""
Comprehensive backend test script
Tests all SaaS features: auth, jobs, batches, templates, scheduling, analytics
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
API_KEY = None  # Will be set from env or use None

# Test results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test(name, func):
    """Run a test and record results"""
    try:
        result = func()
        if result:
            results["passed"].append(name)
            print(f"✅ {name}")
            return result
        else:
            results["failed"].append(name)
            print(f"❌ {name}")
            return None
    except Exception as e:
        results["failed"].append(f"{name}: {str(e)}")
        print(f"❌ {name}: {str(e)}")
        return None

def get_headers(token=None):
    """Get request headers"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if API_KEY:
        headers["X-APP-KEY"] = API_KEY
    return headers

# Test 1: Health Check
def test_health():
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("   Make sure the backend server is running:")
        print("   cd backend && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Test 2: Register User
def test_register():
    data = {
        "email": f"test_{int(time.time())}@test.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    else:
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return None

# Test 3: Login
def test_login(email, password):
    data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/auth/login", json=data, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

# Test 4: List Jobs (with auth)
def test_list_jobs(token):
    response = requests.get(f"{BASE_URL}/jobs?page=1&page_size=10", headers=get_headers(token))
    return response.status_code == 200

# Test 5: Create Template
def test_create_template(token):
    data = {
        "name": "Test Template",
        "subject": "Hello {{name}}",
        "html_body": "<p>Hello {{name}}, welcome to {{company}}!</p>"
    }
    response = requests.post(f"{BASE_URL}/templates", json=data, headers=get_headers(token))
    if response.status_code == 201:
        return response.json()
    return None

# Test 6: List Templates
def test_list_templates(token):
    response = requests.get(f"{BASE_URL}/templates", headers=get_headers(token))
    return response.status_code == 200

# Test 7: Analytics Overview
def test_analytics_overview(token):
    response = requests.get(f"{BASE_URL}/analytics/overview?days=30", headers=get_headers(token))
    if response.status_code != 200:
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    return response.status_code == 200

# Test 8: Batch Progress (without actual batch - should 404)
def test_batch_progress_404(token):
    response = requests.get(
        f"{BASE_URL}/jobs/test-job-id/batches/test-batch-id/progress",
        headers=get_headers(token)
    )
    # Should return 404 for non-existent batch
    return response.status_code == 404

# Test 9: Schedule Endpoint (without actual job - should 404)
def test_schedule_404(token):
    data = {
        "subject": "Test",
        "html_body": "<p>Test</p>",
        "recipients": ["test@example.com"],
        "scheduled_for": (datetime.utcnow() + timedelta(days=1)).isoformat()
    }
    response = requests.post(
        f"{BASE_URL}/jobs/test-job-id/schedule",
        json=data,
        headers=get_headers(token)
    )
    # Should return 404 for non-existent job
    return response.status_code == 404

# Test 10: Refresh Token
def test_refresh_token(refresh_token):
    data = {"refresh_token": refresh_token}
    response = requests.post(f"{BASE_URL}/auth/refresh", json=data, headers=get_headers())
    return response.status_code == 200

print("🧪 Testing AutoMail Backend...")
print("=" * 50)

# Test 1: Health Check
test("Health Check", test_health)

# Test 2: Register
print("\n📝 Testing Authentication...")
register_result = test("User Registration", test_register)
if not register_result:
    print("⚠️  Cannot continue without user registration")
    exit(1)

test_email = register_result["user"]["email"]
test_password = "testpassword123"

# Test 3: Login
login_result = test("User Login", lambda: test_login(test_email, test_password))
if not login_result:
    print("⚠️  Cannot continue without login")
    exit(1)

access_token = login_result["access_token"]
refresh_token = login_result["refresh_token"]

# Test 4: List Jobs
print("\n📋 Testing Jobs...")
test("List Jobs (Authenticated)", lambda: test_list_jobs(access_token))

# Test 5: Create Template
print("\n📧 Testing Templates...")
template_result = test("Create Template", lambda: test_create_template(access_token))
template_id = template_result["id"] if template_result else None

# Test 6: List Templates
test("List Templates", lambda: test_list_templates(access_token))

# Test 7: Analytics
print("\n📊 Testing Analytics...")
test("Analytics Overview", lambda: test_analytics_overview(access_token))

# Test 8: Batch Progress (404 test)
print("\n🔄 Testing Batch APIs...")
test("Batch Progress (404 handling)", lambda: test_batch_progress_404(access_token))

# Test 9: Schedule (404 test)
test("Schedule Endpoint (404 handling)", lambda: test_schedule_404(access_token))

# Test 10: Refresh Token
print("\n🔐 Testing Token Refresh...")
test("Refresh Token", lambda: test_refresh_token(refresh_token))

# Summary
print("\n" + "=" * 50)
print("📊 Test Summary:")
print(f"✅ Passed: {len(results['passed'])}")
print(f"❌ Failed: {len(results['failed'])}")
print(f"⚠️  Warnings: {len(results['warnings'])}")

if results['failed']:
    print("\n❌ Failed Tests:")
    for failure in results['failed']:
        print(f"  - {failure}")

if results['passed']:
    print("\n✅ Passed Tests:")
    for passed in results['passed']:
        print(f"  - {passed}")

print("\n" + "=" * 50)
if len(results['failed']) == 0:
    print("🎉 All tests passed!")
else:
    print(f"⚠️  {len(results['failed'])} test(s) failed")
