#!/usr/bin/env python3
"""
Performance and Stress Testing for Smart Billing System
"""

import requests
import time
import threading
import statistics
from datetime import datetime
import concurrent.futures

class PerformanceStressTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        
    def time_request(self, session, method, url, data=None):
        """Time a single request"""
        start_time = time.time()
        try:
            if method.upper() == 'GET':
                response = session.get(url)
            elif method.upper() == 'POST':
                response = session.post(url, data=data)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code < 400
            }
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return {
                'status_code': 0,
                'response_time': response_time,
                'success': False,
                'error': str(e)
            }
    
    def test_page_load_times(self):
        """Test page load times for key pages"""
        print("⏱️ Testing Page Load Times...")
        
        # Setup admin session
        admin_session = requests.Session()
        admin_session.post(f"{self.base_url}/auth/login", data={
            'email': 'admin@smartbilling.com',
            'password': 'admin123'
        })
        
        # Key pages to test
        pages = [
            ('/dashboard', 'Dashboard'),
            ('/billing/bills', 'Bills List'),
            ('/billing/bills/create', 'Create Invoice'),
            ('/work/entries', 'Work Entries'),
            ('/work/entries/create', 'Create Work Entry'),
            ('/expenses/', 'Expenses'),
            ('/expenses/create', 'Create Expense'),
            ('/settings/profile', 'Profile Settings')
        ]
        
        page_times = {}
        
        for url, name in pages:
            times = []
            for i in range(5):  # Test each page 5 times
                result = self.time_request(admin_session, 'GET', f"{self.base_url}{url}")
                if result['success']:
                    times.append(result['response_time'])
                time.sleep(0.1)  # Small delay between requests
            
            if times:
                avg_time = statistics.mean(times)
                page_times[name] = avg_time
                
                if avg_time < 500:
                    print(f"✅ {name}: {avg_time:.1f}ms (Fast)")
                elif avg_time < 1000:
                    print(f"⚠️ {name}: {avg_time:.1f}ms (Acceptable)")
                else:
                    print(f"❌ {name}: {avg_time:.1f}ms (Slow)")
            else:
                print(f"❌ {name}: Failed to load")
        
        return page_times
    
    def test_concurrent_users(self, num_users=10):
        """Test concurrent user access"""
        print(f"\n👥 Testing {num_users} Concurrent Users...")
        
        def user_session_test(user_id):
            """Simulate a user session"""
            session = requests.Session()
            results = []
            
            # Register user
            reg_data = {
                'username': f'stresstest_{user_id}_{int(time.time())}',
                'email': f'stresstest_{user_id}_{int(time.time())}@example.com',
                'password': 'password123',
                'confirm_password': 'password123',
                'phone': '9876543210'
            }
            
            reg_result = self.time_request(session, 'POST', f"{self.base_url}/auth/register", reg_data)
            results.append(('Registration', reg_result))
            
            if reg_result['success']:
                # Access dashboard
                dash_result = self.time_request(session, 'GET', f"{self.base_url}/dashboard")
                results.append(('Dashboard', dash_result))
                
                # Access bills
                bills_result = self.time_request(session, 'GET', f"{self.base_url}/billing/bills")
                results.append(('Bills', bills_result))
                
                # Create invoice
                invoice_data = {
                    'customer_name': f'Stress Test Customer {user_id}',
                    'customer_email': f'customer_{user_id}@example.com',
                    'customer_contact': '9876543210',
                    'advance_amount': '100',
                    'item_description_1': 'Stress Test Service',
                    'item_quantity_1': '1',
                    'item_rate_1': '500'
                }
                
                invoice_result = self.time_request(session, 'POST', f"{self.base_url}/billing/bills/create", invoice_data)
                results.append(('Create Invoice', invoice_result))
            
            return results
        
        # Run concurrent user tests
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_session_test, i) for i in range(num_users)]
            all_results = []
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    user_results = future.result()
                    all_results.extend(user_results)
                except Exception as e:
                    print(f"❌ User session failed: {e}")
        
        # Analyze results
        successful_operations = sum(1 for _, result in all_results if result['success'])
        total_operations = len(all_results)
        success_rate = (successful_operations / total_operations) * 100 if total_operations > 0 else 0
        
        response_times = [result['response_time'] for _, result in all_results if result['success']]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            print(f"✅ Success Rate: {success_rate:.1f}%")
            print(f"⏱️ Average Response Time: {avg_response_time:.1f}ms")
            print(f"⏱️ Max Response Time: {max_response_time:.1f}ms")
            print(f"⏱️ Min Response Time: {min_response_time:.1f}ms")
            
            if success_rate >= 95 and avg_response_time < 2000:
                print("✅ Concurrent user test PASSED")
            else:
                print("⚠️ Concurrent user test shows performance issues")
        else:
            print("❌ No successful operations in concurrent test")
    
    def test_database_performance(self):
        """Test database performance with multiple operations"""
        print("\n🗄️ Testing Database Performance...")
        
        admin_session = requests.Session()
        admin_session.post(f"{self.base_url}/auth/login", data={
            'email': 'admin@smartbilling.com',
            'password': 'admin123'
        })
        
        # Test multiple invoice creations
        creation_times = []
        
        for i in range(10):
            invoice_data = {
                'customer_name': f'DB Test Customer {i}',
                'customer_email': f'dbtest_{i}@example.com',
                'customer_contact': '9876543210',
                'advance_amount': '50',
                'item_description_1': f'DB Test Service {i}',
                'item_quantity_1': '1',
                'item_rate_1': '300'
            }
            
            result = self.time_request(admin_session, 'POST', f"{self.base_url}/billing/bills/create", invoice_data)
            if result['success']:
                creation_times.append(result['response_time'])
        
        if creation_times:
            avg_creation_time = statistics.mean(creation_times)
            print(f"✅ Average Invoice Creation Time: {avg_creation_time:.1f}ms")
            
            if avg_creation_time < 1000:
                print("✅ Database performance is good")
            else:
                print("⚠️ Database performance may need optimization")
        
        # Test list page performance with data
        list_result = self.time_request(admin_session, 'GET', f"{self.base_url}/billing/bills")
        if list_result['success']:
            print(f"✅ Bills List Load Time: {list_result['response_time']:.1f}ms")
        
    def test_memory_usage(self):
        """Test for potential memory leaks with repeated requests"""
        print("\n🧠 Testing Memory Usage Pattern...")
        
        admin_session = requests.Session()
        admin_session.post(f"{self.base_url}/auth/login", data={
            'email': 'admin@smartbilling.com',
            'password': 'admin123'
        })
        
        # Make repeated requests to the same endpoint
        times = []
        for i in range(50):
            result = self.time_request(admin_session, 'GET', f"{self.base_url}/dashboard")
            if result['success']:
                times.append(result['response_time'])
            
            if i % 10 == 0:
                print(f"  Completed {i+1}/50 requests...")
        
        if len(times) >= 40:  # Need enough data points
            # Check if response times are increasing (potential memory leak)
            first_10 = statistics.mean(times[:10])
            last_10 = statistics.mean(times[-10:])
            
            increase_percentage = ((last_10 - first_10) / first_10) * 100
            
            print(f"✅ First 10 requests average: {first_10:.1f}ms")
            print(f"✅ Last 10 requests average: {last_10:.1f}ms")
            print(f"📈 Performance change: {increase_percentage:+.1f}%")
            
            if increase_percentage < 20:
                print("✅ No significant performance degradation detected")
            else:
                print("⚠️ Performance degradation detected - possible memory leak")
        else:
            print("❌ Insufficient data for memory usage analysis")
    
    def run_performance_tests(self):
        """Run all performance tests"""
        print("🚀 Starting Performance and Stress Testing")
        print("=" * 50)
        
        start_time = time.time()
        
        # Test page load times
        page_times = self.test_page_load_times()
        
        # Test concurrent users
        self.test_concurrent_users(5)  # Start with 5 concurrent users
        
        # Test database performance
        self.test_database_performance()
        
        # Test memory usage
        self.test_memory_usage()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "=" * 50)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("=" * 50)
        print(f"Total Test Duration: {total_time:.1f} seconds")
        
        if page_times:
            fastest_page = min(page_times.items(), key=lambda x: x[1])
            slowest_page = max(page_times.items(), key=lambda x: x[1])
            
            print(f"🏃 Fastest Page: {fastest_page[0]} ({fastest_page[1]:.1f}ms)")
            print(f"🐌 Slowest Page: {slowest_page[0]} ({slowest_page[1]:.1f}ms)")
        
        print("\n🎯 Performance Recommendations:")
        print("- Monitor response times under load")
        print("- Consider database indexing for large datasets")
        print("- Implement caching for frequently accessed data")
        print("- Monitor memory usage in production")

if __name__ == '__main__':
    tester = PerformanceStressTester()
    tester.run_performance_tests()
