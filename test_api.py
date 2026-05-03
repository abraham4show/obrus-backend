#!/usr/bin/env python3
"""
Test script for Obrus Django Backend API
Run this after starting the development server
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_public_endpoints():
    """Test endpoints that don't require authentication"""
    print("\n=== Testing Public Endpoints ===")

    # Test API docs
    response = requests.get(f"{BASE_URL}/docs/")
    print(f"API Docs: {'✓' if response.status_code == 200 else '✗'}")

    # Test service request creation (public)
    data = {
        "full_name": "Test User",
        "phone": "+1234567890",
        "email": "test@example.com",
        "location": "Test Location",
        "service_type": "manpower",
        "service_details": {"workers_needed": 5, "duration": "3 days"}
    }
    response = requests.post(f"{BASE_URL}/service-requests/", json=data)
    print(f"Create Service Request: {'✓' if response.status_code == 201 else '✗'}")
    if response.status_code == 201:
        print(f"  Created request ID: {response.json().get('id')}")

    # Test job application creation (public)
    # Note: This requires multipart/form-data for file uploads
    print(f"Create Job Application: (test manually with file upload)")

def test_authentication():
    """Test authentication endpoints"""
    print("\n=== Testing Authentication ===")

    # Register
    register_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpassword123",
        "password_confirm": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    print(f"Register: {'✓' if response.status_code == 201 else '✗'}")

    if response.status_code == 201:
        tokens = response.json()
        access_token = tokens.get('access')
        refresh_token = tokens.get('refresh')

        # Test profile
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        print(f"Get Profile: {'✓' if response.status_code == 200 else '✗'}")

        # Test logout
        response = requests.post(f"{BASE_URL}/auth/logout/", 
                                headers=headers, 
                                json={"refresh": refresh_token})
        print(f"Logout: {'✓' if response.status_code == 200 else '✗'}")

        return access_token
    return None

def test_authenticated_endpoints(token):
    """Test endpoints that require authentication"""
    if not token:
        print("\nSkipping authenticated tests - no token available")
        return

    print("\n=== Testing Authenticated Endpoints ===")
    headers = {"Authorization": f"Bearer {token}"}

    # Test my service requests
    response = requests.get(f"{BASE_URL}/service-requests/my-requests/", headers=headers)
    print(f"My Service Requests: {'✓' if response.status_code == 200 else '✗'}")

    # Test my job applications
    response = requests.get(f"{BASE_URL}/job-applications/my-applications/", headers=headers)
    print(f"My Job Applications: {'✓' if response.status_code == 200 else '✗'}")

    # Test notifications
    response = requests.get(f"{BASE_URL}/notifications/", headers=headers)
    print(f"Notifications: {'✓' if response.status_code == 200 else '✗'}")

    # Test notification stats
    response = requests.get(f"{BASE_URL}/notifications/stats/", headers=headers)
    print(f"Notification Stats: {'✓' if response.status_code == 200 else '✗'}")

def test_admin_endpoints(token):
    """Test admin-only endpoints"""
    if not token:
        return

    print("\n=== Testing Admin Endpoints (requires admin user) ===")
    headers = {"Authorization": f"Bearer {token}"}

    # Test service request stats
    response = requests.get(f"{BASE_URL}/service-requests/stats/", headers=headers)
    print(f"Service Request Stats: {'✓' if response.status_code == 200 else '✗ (needs admin)'}")

    # Test job application stats
    response = requests.get(f"{BASE_URL}/job-applications/stats/", headers=headers)
    print(f"Job Application Stats: {'✓' if response.status_code == 200 else '✗ (needs admin)'}")

    # Test list all service requests
    response = requests.get(f"{BASE_URL}/service-requests/", headers=headers)
    print(f"All Service Requests: {'✓' if response.status_code == 200 else '✗ (needs admin)'}")

if __name__ == "__main__":
    print("Testing Obrus Django Backend API...")
    print(f"Base URL: {BASE_URL}")

    try:
        test_public_endpoints()
        token = test_authentication()
        test_authenticated_endpoints(token)
        test_admin_endpoints(token)

        print("\n=== Test Summary ===")
        print("Check marks (✓) indicate successful responses")
        print("Cross marks (✗) indicate failed responses")
        print("\nNote: Some tests require the server to be running")
        print("Note: Admin tests require an admin user")

    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to server. Is it running?")
        print(f"   Try: python manage.py runserver")
    except Exception as e:
        print(f"\n✗ Error: {e}")
