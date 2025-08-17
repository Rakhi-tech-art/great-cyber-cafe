#!/usr/bin/env python3
"""
Test role-based access control via HTTP requests
"""

import requests
from requests.auth import HTTPBasicAuth

def test_role_access():
    """Test role-based access control"""
    base_url = "http://localhost:5000"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("🔐 Testing Role-Based Access Control\n")
    
    try:
        # Test 1: Admin Login and Access
        print("1️⃣ Testing Admin Access:")
        login_data = {
            'email': 'admin@smartbilling.com',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        if login_response.status_code in [200, 302]:
            print("   ✅ Admin login successful")
            
            # Test admin-only routes
            admin_routes = [
                '/dashboard/analytics',
                '/billing/all',
                '/auth/users',
                '/settings'
            ]
            
            for route in admin_routes:
                response = session.get(f"{base_url}{route}")
                if response.status_code == 200:
                    print(f"   ✅ Admin can access {route}")
                else:
                    print(f"   ❌ Admin cannot access {route} (Status: {response.status_code})")
        else:
            print("   ❌ Admin login failed")
        
        # Logout
        session.get(f"{base_url}/auth/logout")
        
        # Test 2: User Registration and Access
        print("\n2️⃣ Testing User Access:")
        
        # Register a new user
        register_data = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'phone': '9876543210'
        }
        
        register_response = session.post(f"{base_url}/auth/register", data=register_data)
        if register_response.status_code in [200, 302]:
            print("   ✅ User registration successful")
            
            # Test user-accessible routes
            user_routes = [
                '/dashboard',
                '/billing/create',
                '/billing/bills',
                '/work/create',
                '/settings/profile'
            ]
            
            for route in user_routes:
                response = session.get(f"{base_url}{route}")
                if response.status_code == 200:
                    print(f"   ✅ User can access {route}")
                else:
                    print(f"   ❌ User cannot access {route} (Status: {response.status_code})")
            
            # Test admin-only routes (should be blocked)
            print("\n   Testing Admin-Only Routes (should be blocked):")
            admin_only_routes = [
                '/dashboard/analytics',
                '/billing/all',
                '/auth/users',
                '/settings'
            ]
            
            for route in admin_only_routes:
                response = session.get(f"{base_url}{route}")
                if response.status_code == 403 or 'admin privileges' in response.text.lower():
                    print(f"   ✅ User correctly blocked from {route}")
                elif response.status_code == 302:
                    print(f"   ✅ User redirected from {route} (protected)")
                else:
                    print(f"   ⚠️  User access to {route} unclear (Status: {response.status_code})")
        else:
            print("   ❌ User registration failed")
        
        print("\n🎉 Role-based access control test completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application. Make sure it's running on localhost:5000")
    except Exception as e:
        print(f"❌ Error testing role access: {e}")

if __name__ == '__main__':
    test_role_access()
