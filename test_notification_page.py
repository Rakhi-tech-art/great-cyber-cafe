#!/usr/bin/env python3
"""
Test the notification settings page functionality
"""

import requests
from requests.auth import HTTPBasicAuth

def test_notification_settings_page():
    """Test the notification settings page"""
    base_url = "http://localhost:5000"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # First, try to access the login page
        login_response = session.get(f"{base_url}/auth/login")
        print(f"✅ Login page accessible: {login_response.status_code}")
        
        # Try to login with admin credentials
        login_data = {
            'email': 'admin@smartbilling.com',
            'password': 'admin123'
        }
        
        login_post = session.post(f"{base_url}/auth/login", data=login_data)
        print(f"✅ Login attempt: {login_post.status_code}")
        
        # Now try to access the notification settings page
        settings_response = session.get(f"{base_url}/settings/notifications")
        print(f"✅ Notification settings page: {settings_response.status_code}")
        
        if settings_response.status_code == 200:
            print("✅ Notification settings page is accessible!")
            
            # Check if the page contains expected elements
            content = settings_response.text
            if "Email Notifications" in content:
                print("✅ Email notifications section found")
            if "WhatsApp Notifications" in content:
                print("✅ WhatsApp notifications section found")
            if "Notification Schedule" in content:
                print("✅ Notification schedule section found")
            if "email_bill_created" in content:
                print("✅ Form fields are present")
            
            # Test form submission
            form_data = {
                'email_bill_created': 'on',
                'email_bill_paid': 'on',
                'whatsapp_bill_paid': 'on',
                'quiet_hours_start': '22:00',
                'quiet_hours_end': '08:00',
                'weekly_report_day': 'monday',
                'report_time': '09:00'
            }
            
            post_response = session.post(f"{base_url}/settings/notifications", data=form_data)
            print(f"✅ Form submission: {post_response.status_code}")
            
            if post_response.status_code in [200, 302]:  # 302 for redirect
                print("✅ Form submission successful!")
            else:
                print(f"❌ Form submission failed: {post_response.status_code}")
        
        else:
            print(f"❌ Could not access notification settings page: {settings_response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application. Make sure it's running on localhost:5000")
    except Exception as e:
        print(f"❌ Error testing notification settings: {e}")

if __name__ == '__main__':
    test_notification_settings_page()
