#!/usr/bin/env python3
"""
Test PDF generation and email functionality
"""

import requests
import time
import os

def test_pdf_email_features():
    base_url = "http://localhost:5000"
    
    # Admin session
    admin_session = requests.Session()
    
    # Login as admin
    login_response = admin_session.post(f"{base_url}/auth/login", data={
        'email': 'admin@smartbilling.com',
        'password': 'admin123'
    })
    
    if login_response.status_code not in [200, 302]:
        print("❌ Could not login as admin")
        return
    
    print("✅ Admin login successful")
    
    # Create a test invoice first
    invoice_data = {
        'customer_name': 'PDF Test Customer',
        'customer_email': 'pdftest@example.com',
        'customer_contact': '9876543210',
        'advance_amount': '100',
        'item_description_1': 'Test Service',
        'item_quantity_1': '1',
        'item_rate_1': '1000'
    }
    
    create_response = admin_session.post(f"{base_url}/billing/bills/create", data=invoice_data)
    
    if create_response.status_code in [200, 302]:
        print("✅ Test invoice created")
        
        # Extract bill ID from redirect URL
        if '/billing/bills/' in create_response.url:
            bill_id = create_response.url.split('/billing/bills/')[-1]
            print(f"✅ Bill ID extracted: {bill_id}")
            
            # Test PDF generation
            pdf_response = admin_session.get(f"{base_url}/billing/bills/{bill_id}/pdf")
            
            if pdf_response.status_code == 200:
                if pdf_response.headers.get('content-type') == 'application/pdf':
                    print("✅ PDF generation working - correct content type")
                    
                    # Check PDF size (should be reasonable)
                    pdf_size = len(pdf_response.content)
                    if pdf_size > 1000:  # At least 1KB
                        print(f"✅ PDF size reasonable: {pdf_size} bytes")
                    else:
                        print(f"⚠️ PDF size seems small: {pdf_size} bytes")
                else:
                    print(f"❌ PDF generation failed - wrong content type: {pdf_response.headers.get('content-type')}")
            else:
                print(f"❌ PDF generation failed - status: {pdf_response.status_code}")
            
            # Test email sending (this will test the endpoint, actual email sending depends on configuration)
            email_data = {
                'recipient_email': 'test@example.com',
                'message': 'Test email message'
            }
            
            email_response = admin_session.post(f"{base_url}/billing/bills/{bill_id}/send-email", data=email_data)
            
            if email_response.status_code in [200, 302]:
                print("✅ Email sending endpoint working")
            else:
                print(f"⚠️ Email sending endpoint returned: {email_response.status_code}")
            
            # Test WhatsApp sending endpoint
            whatsapp_data = {
                'phone_number': '9876543210',
                'message': 'Test WhatsApp message'
            }
            
            whatsapp_response = admin_session.post(f"{base_url}/billing/bills/{bill_id}/send-whatsapp", data=whatsapp_data)
            
            if whatsapp_response.status_code in [200, 302]:
                print("✅ WhatsApp sending endpoint working")
            else:
                print(f"⚠️ WhatsApp sending endpoint returned: {whatsapp_response.status_code}")
                
        else:
            print("❌ Could not extract bill ID from response")
    else:
        print("❌ Could not create test invoice")
    
    # Test notification test endpoint
    test_notification_response = admin_session.post(f"{base_url}/api/settings/test-notification")
    
    if test_notification_response.status_code == 200:
        try:
            response_data = test_notification_response.json()
            if response_data.get('success'):
                print("✅ Test notification endpoint working")
            else:
                print(f"⚠️ Test notification failed: {response_data.get('message')}")
        except:
            print("⚠️ Test notification response not JSON")
    else:
        print(f"❌ Test notification endpoint failed: {test_notification_response.status_code}")

def test_file_upload_features():
    """Test file upload functionality"""
    base_url = "http://localhost:5000"
    
    # Admin session
    admin_session = requests.Session()
    
    # Login as admin
    login_response = admin_session.post(f"{base_url}/auth/login", data={
        'email': 'admin@smartbilling.com',
        'password': 'admin123'
    })
    
    if login_response.status_code not in [200, 302]:
        print("❌ Could not login as admin for file upload test")
        return
    
    # Test profile picture upload (if endpoint exists)
    profile_response = admin_session.get(f"{base_url}/settings/profile")
    
    if profile_response.status_code == 200:
        if 'profile_picture' in profile_response.text or 'avatar' in profile_response.text:
            print("✅ Profile picture upload feature detected")
        else:
            print("ℹ️ No profile picture upload feature found")
    
    print("✅ File upload features tested")

def test_data_export_features():
    """Test data export functionality"""
    base_url = "http://localhost:5000"
    
    # Admin session
    admin_session = requests.Session()
    
    # Login as admin
    login_response = admin_session.post(f"{base_url}/auth/login", data={
        'email': 'admin@smartbilling.com',
        'password': 'admin123'
    })
    
    if login_response.status_code not in [200, 302]:
        print("❌ Could not login as admin for export test")
        return
    
    # Test various export endpoints
    export_types = ['bills', 'expenses', 'work', 'all']
    
    for export_type in export_types:
        export_response = admin_session.get(f"{base_url}/export/{export_type}")
        
        if export_response.status_code == 200:
            if 'text/csv' in export_response.headers.get('content-type', ''):
                print(f"✅ {export_type.title()} export working (CSV)")
            else:
                print(f"⚠️ {export_type.title()} export returned non-CSV content")
        else:
            print(f"❌ {export_type.title()} export failed: {export_response.status_code}")

if __name__ == '__main__':
    print("🧪 Testing PDF and Email Features")
    print("=" * 40)
    
    test_pdf_email_features()
    
    print("\n📁 Testing File Upload Features")
    print("=" * 40)
    
    test_file_upload_features()
    
    print("\n📊 Testing Data Export Features")
    print("=" * 40)
    
    test_data_export_features()
    
    print("\n🎉 PDF, Email, and File Testing Complete!")
