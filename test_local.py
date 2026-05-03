#!/usr/bin/env python3
"""
Quick test to verify Django backend is working
Run this after starting the server
"""

import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def test_api():
    print("Testing Obrus Django Backend...")
    print(f"Base URL: {BASE_URL}\n")

    tests = []

    # Test 1: API Docs
    try:
        response = requests.get(f"{BASE_URL}/docs/", timeout=5)
        tests.append(("API Documentation", response.status_code == 200))
    except:
        tests.append(("API Documentation", False))

    # Test 2: Schema
    try:
        response = requests.get(f"{BASE_URL}/schema/", timeout=5)
        tests.append(("API Schema", response.status_code == 200))
    except:
        tests.append(("API Schema", False))

    # Test 3: Service Request (Public)
    try:
        data = {
            "full_name": "Test User",
            "phone": "+1234567890",
            "email": "test@example.com",
            "location": "Test Location",
            "service_type": "manpower",
            "service_details": {"test": "data"}
        }
        response = requests.post(f"{BASE_URL}/service-requests/", json=data, timeout=5)
        tests.append(("Create Service Request (Public)", response.status_code == 201))
        if response.status_code == 201:
            print(f"  Created request ID: {response.json().get('id')}")
    except Exception as e:
        tests.append(("Create Service Request (Public)", False))
        print(f"  Error: {e}")

    # Print results
    print("\n=== Test Results ===")
    for name, passed in tests:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(passed for _, passed in tests)

    if all_passed:
        print("\n🎉 All tests passed! Your backend is working correctly.")
        print("\nNext steps:")
        print("1. Open http://127.0.0.1:8000/api/docs/ in your browser")
        print("2. Log in to admin at http://127.0.0.1:8000/admin/")
        print("3. Connect your React frontend to the API")
    else:
        print("\n⚠️  Some tests failed. Make sure the server is running:")
        print("   python manage.py runserver")

    return all_passed

if __name__ == "__main__":
    try:
        success = test_api()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
