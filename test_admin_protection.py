#!/usr/bin/env python3
"""
Test admin protection specifically
"""

import requests
import time

def test_admin_protection():
    base_url = "http://localhost:5000"
    
    # Create user session
    user_session = requests.Session()
    
    # Register a new user
    timestamp = int(time.time())
    reg_data = {
        'username': f'testuser_{timestamp}',
        'email': f'testuser_{timestamp}@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'phone': '9876543210'
    }
    
    reg_response = user_session.post(f"{base_url}/auth/register", data=reg_data)
    print(f"User registration: {reg_response.status_code}")
    
    # Test access to admin-only route
    admin_route_response = user_session.get(f"{base_url}/billing/all")
    print(f"User access to /billing/all: {admin_route_response.status_code}")
    print(f"Response URL: {admin_route_response.url}")
    
    # Check response content for admin privilege message
    if 'admin privileges' in admin_route_response.text.lower():
        print("✅ User correctly blocked with admin privilege message")
    elif admin_route_response.status_code == 302:
        print("✅ User redirected (likely blocked)")
    elif admin_route_response.status_code == 200:
        print("❌ User can access admin route (SECURITY ISSUE)")
        # Check if it's actually showing admin content
        if 'All Invoices' in admin_route_response.text:
            print("❌ User can see admin content")
        else:
            print("⚠️ User gets 200 but may not see admin content")
    else:
        print(f"⚠️ Unexpected response: {admin_route_response.status_code}")

if __name__ == '__main__':
    test_admin_protection()
