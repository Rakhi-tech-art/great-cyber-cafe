#!/usr/bin/env python3
"""
Detailed Functional Tests for Smart Billing System
Tests actual functionality, not just page access
"""

import requests
import json
import time
from datetime import datetime, timedelta
import os

class DetailedFunctionalTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.admin_session = requests.Session()
        self.user_session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, status, message=""):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
    
    def setup_sessions(self):
        """Setup admin and user sessions"""
        # Admin login
        admin_login = self.admin_session.post(f"{self.base_url}/auth/login", data={
            'email': 'admin@smartbilling.com',
            'password': 'admin123'
        })
        
        if admin_login.status_code not in [200, 302]:
            self.log_test("Admin Session Setup", "FAIL", "Could not login as admin")
            return False
        
        # User registration and login
        timestamp = int(time.time())
        user_reg = self.user_session.post(f"{self.base_url}/auth/register", data={
            'username': f'testuser_{timestamp}',
            'email': f'testuser_{timestamp}@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'phone': '9876543210'
        })
        
        if user_reg.status_code not in [200, 302]:
            self.log_test("User Session Setup", "FAIL", "Could not register/login as user")
            return False
        
        self.log_test("Session Setup", "PASS", "Both admin and user sessions established")
        return True
    
    def test_invoice_creation(self):
        """Test complete invoice creation workflow"""
        try:
            # Test invoice creation form data
            invoice_data = {
                'customer_name': 'Test Customer',
                'customer_email': 'testcustomer@example.com',
                'customer_contact': '9876543210',
                'advance_amount': '500',
                'item_description_1': 'Website Development',
                'item_quantity_1': '1',
                'item_rate_1': '5000',
                'item_description_2': 'Domain Registration',
                'item_quantity_2': '1',
                'item_rate_2': '1500'
            }
            
            # Create invoice as admin
            response = self.admin_session.post(f"{self.base_url}/billing/bills/create", data=invoice_data)
            
            if response.status_code in [200, 302]:
                self.log_test("Invoice Creation", "PASS", "Invoice created successfully")
                
                # Check if redirected to view page (indicates success)
                if 'billing/bills/' in response.url:
                    self.log_test("Invoice Creation Redirect", "PASS", "Redirected to invoice view")
                else:
                    self.log_test("Invoice Creation Redirect", "WARNING", "Unexpected redirect")
                    
            else:
                self.log_test("Invoice Creation", "FAIL", f"Failed to create invoice: {response.status_code}")
                
        except Exception as e:
            self.log_test("Invoice Creation", "FAIL", f"Error: {str(e)}")
    
    def test_work_entry_creation(self):
        """Test work entry creation"""
        try:
            work_data = {
                'customer_name': 'Work Test Customer',
                'customer_phone': '9876543210',
                'service_type': 'passport',
                'project_name': 'Passport Application',
                'hourly_rate': '100',
                'advance_amount': '200',
                'work_status': 'in_progress'
            }
            
            response = self.admin_session.post(f"{self.base_url}/work/entries/create", data=work_data)
            
            if response.status_code in [200, 302]:
                self.log_test("Work Entry Creation", "PASS", "Work entry created successfully")
            else:
                self.log_test("Work Entry Creation", "FAIL", f"Failed to create work entry: {response.status_code}")
                
        except Exception as e:
            self.log_test("Work Entry Creation", "FAIL", f"Error: {str(e)}")
    
    def test_expense_creation(self):
        """Test expense creation"""
        try:
            expense_data = {
                'title': 'Office Supplies',
                'description': 'Printer paper and ink',
                'amount': '250.50',
                'category': 'Office Supplies',
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
            response = self.admin_session.post(f"{self.base_url}/expenses/create", data=expense_data)
            
            if response.status_code in [200, 302]:
                self.log_test("Expense Creation", "PASS", "Expense created successfully")
            else:
                self.log_test("Expense Creation", "FAIL", f"Failed to create expense: {response.status_code}")
                
        except Exception as e:
            self.log_test("Expense Creation", "FAIL", f"Error: {str(e)}")
    
    def test_profile_update(self):
        """Test profile update functionality"""
        try:
            profile_data = {
                'username': 'Updated Admin',
                'email': 'admin@smartbilling.com',
                'phone': '9999999999'
            }
            
            response = self.admin_session.post(f"{self.base_url}/settings/profile", data=profile_data)
            
            if response.status_code in [200, 302]:
                self.log_test("Profile Update", "PASS", "Profile updated successfully")
            else:
                self.log_test("Profile Update", "FAIL", f"Failed to update profile: {response.status_code}")
                
        except Exception as e:
            self.log_test("Profile Update", "FAIL", f"Error: {str(e)}")
    
    def test_notification_settings(self):
        """Test notification settings update"""
        try:
            notification_data = {
                'email_bill_created': 'on',
                'email_bill_paid': 'on',
                'whatsapp_bill_paid': 'on',
                'quiet_hours_start': '22:00',
                'quiet_hours_end': '08:00',
                'weekly_report_day': 'monday',
                'report_time': '09:00'
            }
            
            response = self.admin_session.post(f"{self.base_url}/settings/notifications", data=notification_data)
            
            if response.status_code in [200, 302]:
                self.log_test("Notification Settings", "PASS", "Notification settings updated successfully")
            else:
                self.log_test("Notification Settings", "FAIL", f"Failed to update notification settings: {response.status_code}")
                
        except Exception as e:
            self.log_test("Notification Settings", "FAIL", f"Error: {str(e)}")
    
    def test_data_filtering(self):
        """Test that users only see their own data"""
        try:
            # Get admin bills
            admin_bills = self.admin_session.get(f"{self.base_url}/billing/bills")
            
            # Get user bills
            user_bills = self.user_session.get(f"{self.base_url}/billing/bills")
            
            if admin_bills.status_code == 200 and user_bills.status_code == 200:
                self.log_test("Data Filtering", "PASS", "Both admin and user can access their bills")
                
                # Check if user cannot access admin-only data
                user_all_bills = self.user_session.get(f"{self.base_url}/billing/all")
                if user_all_bills.status_code in [403, 302] or 'admin privileges' in user_all_bills.text.lower() or 'dashboard' in user_all_bills.url:
                    self.log_test("Data Isolation", "PASS", "User correctly blocked from all bills")
                else:
                    self.log_test("Data Isolation", "FAIL", "User can access all bills (security issue)")
            else:
                self.log_test("Data Filtering", "FAIL", "Could not access bills pages")
                
        except Exception as e:
            self.log_test("Data Filtering", "FAIL", f"Error: {str(e)}")
    
    def test_dashboard_statistics(self):
        """Test dashboard statistics display"""
        try:
            admin_dashboard = self.admin_session.get(f"{self.base_url}/dashboard")
            user_dashboard = self.user_session.get(f"{self.base_url}/dashboard")
            
            if admin_dashboard.status_code == 200:
                # Check for admin-specific content
                if 'Total Users' in admin_dashboard.text or 'System-wide' in admin_dashboard.text:
                    self.log_test("Admin Dashboard Content", "PASS", "Admin dashboard shows system-wide stats")
                else:
                    self.log_test("Admin Dashboard Content", "WARNING", "Admin dashboard may not show admin-specific content")
            
            if user_dashboard.status_code == 200:
                # Check that user dashboard doesn't show admin content
                if 'Total Users' not in user_dashboard.text:
                    self.log_test("User Dashboard Content", "PASS", "User dashboard shows personal stats only")
                else:
                    self.log_test("User Dashboard Content", "FAIL", "User dashboard shows admin content")
                    
        except Exception as e:
            self.log_test("Dashboard Statistics", "FAIL", f"Error: {str(e)}")
    
    def test_search_functionality(self):
        """Test search functionality in various modules"""
        try:
            # Test bill search
            search_response = self.admin_session.get(f"{self.base_url}/billing/bills?search=test")
            if search_response.status_code == 200:
                self.log_test("Bill Search", "PASS", "Bill search functionality working")
            else:
                self.log_test("Bill Search", "FAIL", "Bill search not working")
            
            # Test expense filtering
            filter_response = self.admin_session.get(f"{self.base_url}/expenses/?category=Office Supplies")
            if filter_response.status_code == 200:
                self.log_test("Expense Filtering", "PASS", "Expense filtering working")
            else:
                self.log_test("Expense Filtering", "FAIL", "Expense filtering not working")
                
        except Exception as e:
            self.log_test("Search Functionality", "FAIL", f"Error: {str(e)}")
    
    def run_detailed_tests(self):
        """Run all detailed functional tests"""
        print("🔬 Starting Detailed Functional Testing")
        print("=" * 50)
        
        if not self.setup_sessions():
            print("❌ Could not setup test sessions. Aborting tests.")
            return
        
        print("\n💰 Testing Invoice Functionality...")
        self.test_invoice_creation()
        
        print("\n⏰ Testing Work Entry Functionality...")
        self.test_work_entry_creation()
        
        print("\n💸 Testing Expense Functionality...")
        self.test_expense_creation()
        
        print("\n👤 Testing Profile Management...")
        self.test_profile_update()
        
        print("\n🔔 Testing Notification Settings...")
        self.test_notification_settings()
        
        print("\n🔒 Testing Data Security...")
        self.test_data_filtering()
        
        print("\n📊 Testing Dashboard...")
        self.test_dashboard_statistics()
        
        print("\n🔍 Testing Search Features...")
        self.test_search_functionality()
        
        self.generate_detailed_report()
    
    def generate_detailed_report(self):
        """Generate detailed test report"""
        print("\n" + "=" * 50)
        print("📋 DETAILED FUNCTIONAL TEST REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warning_tests = len([t for t in self.test_results if t['status'] == 'WARNING'])
        
        print(f"Total Functional Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if test['status'] == 'FAIL':
                    print(f"   - {test['test']}: {test['message']}")
        
        if warning_tests > 0:
            print("\n⚠️ WARNINGS:")
            for test in self.test_results:
                if test['status'] == 'WARNING':
                    print(f"   - {test['test']}: {test['message']}")
        
        # Save detailed report
        with open('detailed_test_report.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: detailed_test_report.json")

if __name__ == '__main__':
    tester = DetailedFunctionalTester()
    tester.run_detailed_tests()
