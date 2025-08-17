#!/usr/bin/env python3
"""
Comprehensive Test Suite for Smart Billing System
Tests all major functionalities and features before deployment
"""

import requests
import json
import time
from datetime import datetime, timedelta
import os

class SmartBillingTester:
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
        
    def test_server_connectivity(self):
        """Test if server is running and accessible"""
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code in [200, 302]:
                self.log_test("Server Connectivity", "PASS", "Server is running and accessible")
                return True
            else:
                self.log_test("Server Connectivity", "FAIL", f"Server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_test("Server Connectivity", "FAIL", "Cannot connect to server")
            return False
        except Exception as e:
            self.log_test("Server Connectivity", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_admin_authentication(self):
        """Test admin login functionality"""
        try:
            # Test login page access
            login_page = self.admin_session.get(f"{self.base_url}/auth/login")
            if login_page.status_code != 200:
                self.log_test("Admin Login Page", "FAIL", f"Login page not accessible: {login_page.status_code}")
                return False
            
            self.log_test("Admin Login Page", "PASS", "Login page accessible")
            
            # Test admin login
            login_data = {
                'email': 'admin@smartbilling.com',
                'password': 'admin123'
            }
            
            login_response = self.admin_session.post(f"{self.base_url}/auth/login", data=login_data)
            if login_response.status_code in [200, 302]:
                self.log_test("Admin Authentication", "PASS", "Admin login successful")
                return True
            else:
                self.log_test("Admin Authentication", "FAIL", f"Login failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration functionality"""
        try:
            # Test registration page access
            reg_page = self.user_session.get(f"{self.base_url}/auth/register")
            if reg_page.status_code != 200:
                self.log_test("User Registration Page", "FAIL", f"Registration page not accessible: {reg_page.status_code}")
                return False
            
            self.log_test("User Registration Page", "PASS", "Registration page accessible")
            
            # Test user registration
            timestamp = int(time.time())
            reg_data = {
                'username': f'testuser_{timestamp}',
                'email': f'testuser_{timestamp}@example.com',
                'password': 'password123',
                'confirm_password': 'password123',
                'phone': '9876543210'
            }
            
            reg_response = self.user_session.post(f"{self.base_url}/auth/register", data=reg_data)
            if reg_response.status_code in [200, 302]:
                self.log_test("User Registration", "PASS", "User registration successful")
                return True
            else:
                self.log_test("User Registration", "FAIL", f"Registration failed: {reg_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_dashboard_access(self):
        """Test dashboard access for both admin and user"""
        try:
            # Test admin dashboard
            admin_dashboard = self.admin_session.get(f"{self.base_url}/dashboard")
            if admin_dashboard.status_code == 200:
                self.log_test("Admin Dashboard", "PASS", "Admin dashboard accessible")
            else:
                self.log_test("Admin Dashboard", "FAIL", f"Admin dashboard not accessible: {admin_dashboard.status_code}")
            
            # Test user dashboard
            user_dashboard = self.user_session.get(f"{self.base_url}/dashboard")
            if user_dashboard.status_code == 200:
                self.log_test("User Dashboard", "PASS", "User dashboard accessible")
            else:
                self.log_test("User Dashboard", "FAIL", f"User dashboard not accessible: {user_dashboard.status_code}")
                
        except Exception as e:
            self.log_test("Dashboard Access", "FAIL", f"Error: {str(e)}")
    
    def test_billing_functionality(self):
        """Test billing system functionality"""
        try:
            # Test billing pages access
            pages = [
                ('/billing/bills/create', 'Create Invoice Page'),
                ('/billing/bills', 'Bills List Page'),
                ('/billing/customers', 'Customers Page')
            ]
            
            for url, name in pages:
                response = self.admin_session.get(f"{self.base_url}{url}")
                if response.status_code == 200:
                    self.log_test(name, "PASS", f"{name} accessible")
                else:
                    self.log_test(name, "FAIL", f"{name} not accessible: {response.status_code}")
                    
        except Exception as e:
            self.log_test("Billing Functionality", "FAIL", f"Error: {str(e)}")
    
    def test_work_tracker(self):
        """Test work tracker functionality"""
        try:
            # Test work tracker pages
            pages = [
                ('/work/entries', 'Work Entries Page'),
                ('/work/entries/create', 'Create Work Entry Page'),
                ('/work/timer', 'Work Timer Page')
            ]
            
            for url, name in pages:
                response = self.admin_session.get(f"{self.base_url}{url}")
                if response.status_code == 200:
                    self.log_test(name, "PASS", f"{name} accessible")
                else:
                    self.log_test(name, "FAIL", f"{name} not accessible: {response.status_code}")
                    
        except Exception as e:
            self.log_test("Work Tracker", "FAIL", f"Error: {str(e)}")
    
    def test_expense_tracker(self):
        """Test expense tracker functionality"""
        try:
            # Test expense tracker pages
            pages = [
                ('/expenses/', 'Expenses Page'),
                ('/expenses/create', 'Create Expense Page'),
                ('/expenses/reports', 'Expense Reports Page')
            ]
            
            for url, name in pages:
                response = self.admin_session.get(f"{self.base_url}{url}")
                if response.status_code == 200:
                    self.log_test(name, "PASS", f"{name} accessible")
                else:
                    self.log_test(name, "FAIL", f"{name} not accessible: {response.status_code}")
                    
        except Exception as e:
            self.log_test("Expense Tracker", "FAIL", f"Error: {str(e)}")
    
    def test_settings_functionality(self):
        """Test settings functionality"""
        try:
            # Test settings pages
            pages = [
                ('/settings/profile', 'Profile Settings'),
                ('/settings/password', 'Password Settings'),
                ('/settings/appearance', 'Appearance Settings'),
                ('/settings/notifications', 'Notification Settings')
            ]
            
            for url, name in pages:
                response = self.admin_session.get(f"{self.base_url}{url}")
                if response.status_code == 200:
                    self.log_test(name, "PASS", f"{name} accessible")
                else:
                    self.log_test(name, "FAIL", f"{name} not accessible: {response.status_code}")
                    
        except Exception as e:
            self.log_test("Settings Functionality", "FAIL", f"Error: {str(e)}")
    
    def test_role_based_access(self):
        """Test role-based access control"""
        try:
            # Admin-only routes that users should not access
            admin_only_routes = [
                ('/dashboard/analytics', 'Analytics'),
                ('/billing/all', 'All Invoices'),
                ('/auth/users', 'User Management'),
                ('/settings', 'System Settings')
            ]
            
            for url, name in admin_only_routes:
                # Test admin access
                admin_response = self.admin_session.get(f"{self.base_url}{url}")
                if admin_response.status_code == 200:
                    self.log_test(f"Admin Access to {name}", "PASS", f"Admin can access {name}")
                else:
                    self.log_test(f"Admin Access to {name}", "FAIL", f"Admin cannot access {name}")
                
                # Test user access (should be blocked)
                user_response = self.user_session.get(f"{self.base_url}{url}")
                if user_response.status_code in [403, 302] or 'admin privileges' in user_response.text.lower():
                    self.log_test(f"User Blocked from {name}", "PASS", f"User correctly blocked from {name}")
                else:
                    self.log_test(f"User Blocked from {name}", "FAIL", f"User can access {name} (should be blocked)")
                    
        except Exception as e:
            self.log_test("Role-Based Access", "FAIL", f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🧪 Starting Comprehensive Testing of Smart Billing System")
        print("=" * 60)
        
        # Check server connectivity first
        if not self.test_server_connectivity():
            print("❌ Server not accessible. Please start the application first.")
            return
        
        # Run authentication tests
        print("\n🔐 Testing Authentication & User Management...")
        self.test_admin_authentication()
        self.test_user_registration()
        
        # Run dashboard tests
        print("\n📊 Testing Dashboard Access...")
        self.test_dashboard_access()
        
        # Run feature tests
        print("\n💰 Testing Billing System...")
        self.test_billing_functionality()
        
        print("\n⏰ Testing Work Tracker...")
        self.test_work_tracker()
        
        print("\n💸 Testing Expense Tracker...")
        self.test_expense_tracker()
        
        print("\n⚙️ Testing Settings...")
        self.test_settings_functionality()
        
        print("\n🛡️ Testing Role-Based Access Control...")
        self.test_role_based_access()
        
        # Generate summary
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warning_tests = len([t for t in self.test_results if t['status'] == 'WARNING'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if test['status'] == 'FAIL':
                    print(f"   - {test['test']}: {test['message']}")
        
        # Save detailed report
        with open('test_report.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: test_report.json")
        
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Your application is ready for deployment.")
        else:
            print(f"\n⚠️ {failed_tests} tests failed. Please fix these issues before deployment.")

if __name__ == '__main__':
    tester = SmartBillingTester()
    tester.run_all_tests()
