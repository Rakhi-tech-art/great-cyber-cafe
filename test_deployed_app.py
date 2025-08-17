#!/usr/bin/env python3
"""
Test Deployed Application
Quick health check for the deployed Smart Billing System
"""

import requests
import sys
from datetime import datetime

def test_deployment(base_url):
    """Test the deployed application"""
    print(f"🧪 Testing Deployed Application: {base_url}")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Basic connectivity
    print("\n🌐 Testing Basic Connectivity...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Application is accessible")
            tests_passed += 1
        else:
            print(f"❌ Application returned status code: {response.status_code}")
            tests_failed += 1
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        tests_failed += 1
        return tests_passed, tests_failed
    
    # Test 2: Login page
    print("\n🔐 Testing Login Page...")
    try:
        response = requests.get(f"{base_url}/auth/login", timeout=10)
        if response.status_code == 200 and "login" in response.text.lower():
            print("✅ Login page loads correctly")
            tests_passed += 1
        else:
            print("❌ Login page not accessible")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Login page test failed: {e}")
        tests_failed += 1
    
    # Test 3: Static files
    print("\n📁 Testing Static Files...")
    try:
        response = requests.get(f"{base_url}/static/css/style.css", timeout=10)
        if response.status_code == 200:
            print("✅ Static files are accessible")
            tests_passed += 1
        else:
            print("❌ Static files not accessible")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Static files test failed: {e}")
        tests_failed += 1
    
    # Test 4: API endpoints (basic)
    print("\n🔌 Testing API Endpoints...")
    try:
        # Test a simple endpoint that should redirect to login
        response = requests.get(f"{base_url}/dashboard", timeout=10, allow_redirects=False)
        if response.status_code in [302, 401]:  # Redirect to login or unauthorized
            print("✅ Protected routes are properly secured")
            tests_passed += 1
        else:
            print("❌ Protected routes may not be properly secured")
            tests_failed += 1
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        tests_failed += 1
    
    # Test 5: Database connectivity (indirect)
    print("\n🗄️ Testing Database Connectivity...")
    try:
        # Try to access a page that would require database
        response = requests.get(f"{base_url}/auth/register", timeout=10)
        if response.status_code == 200:
            print("✅ Database-dependent pages load correctly")
            tests_passed += 1
        else:
            print("❌ Database-dependent pages may have issues")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Database connectivity test failed: {e}")
        tests_failed += 1
    
    # Test 6: Response time
    print("\n⏱️ Testing Response Time...")
    try:
        start_time = datetime.now()
        response = requests.get(base_url, timeout=10)
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        if response_time < 5.0:
            print(f"✅ Good response time: {response_time:.2f} seconds")
            tests_passed += 1
        elif response_time < 10.0:
            print(f"⚠️ Acceptable response time: {response_time:.2f} seconds")
            tests_passed += 1
        else:
            print(f"❌ Slow response time: {response_time:.2f} seconds")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Response time test failed: {e}")
        tests_failed += 1
    
    return tests_passed, tests_failed

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python test_deployed_app.py <your-app-url>")
        print("Example: python test_deployed_app.py https://great-cyber-cafe.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    # Validate URL format
    if not base_url.startswith(('http://', 'https://')):
        print("❌ Please provide a complete URL starting with http:// or https://")
        sys.exit(1)
    
    # Run tests
    passed, failed = test_deployment(base_url)
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your application is ready for use.")
        print("\n🔗 Next Steps:")
        print(f"   1. Visit: {base_url}")
        print("   2. Login with: admin@smartbilling.com / admin123")
        print("   3. Change the default admin password")
        print("   4. Start using your Smart Billing System!")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please check the deployment.")
        print("\n🔧 Troubleshooting:")
        print("   1. Check Render deployment logs")
        print("   2. Verify environment variables are set")
        print("   3. Ensure database is connected")
        print("   4. Check for any build errors")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
