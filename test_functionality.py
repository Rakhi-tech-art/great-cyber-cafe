import requests
import json
import sys

base_url = 'http://localhost:5000'

# Create a session to maintain cookies
session = requests.Session()

def test_login():
    print("🔐 Testing login...")
    login_data = {
        'email': 'admin@smartbilling.com',
        'password': 'admin123'
    }
    
    response = session.post(f'{base_url}/auth/login', data=login_data)
    if response.status_code == 200 and 'dashboard' in response.url:
        print("✅ Login successful!")
        return True
    else:
        print(f"❌ Login failed: {response.status_code}")
        return False

def test_create_bill():
    print("\n📄 Testing bill creation...")
    
    # Test GET request to create page
    response = session.get(f'{base_url}/billing/bills/create')
    if response.status_code != 200:
        print(f"❌ Cannot access create page: {response.status_code}")
        return False
    
    # Test POST request to create a bill
    bill_data = {
        'customer_name': 'Test Customer',
        'customer_email': 'test@example.com',
        'customer_phone': '1234567890',
        'items[0][description]': 'Test Service',
        'items[0][quantity]': '1',
        'items[0][rate]': '100.00',
        'tax_rate': '18',
        'discount': '0',
        'notes': 'Test bill created by automated test'
    }
    
    response = session.post(f'{base_url}/billing/bills/create', data=bill_data)
    if response.status_code == 200 or (response.status_code == 302 and 'billing' in response.headers.get('Location', '')):
        print("✅ Bill creation successful!")
        return True
    else:
        print(f"❌ Bill creation failed: {response.status_code}")
        return False

def test_view_bills():
    print("\n📋 Testing bill listing...")
    
    response = session.get(f'{base_url}/billing/bills')
    if response.status_code == 200:
        print("✅ Bills page loads successfully!")
        return True
    else:
        print(f"❌ Bills page failed: {response.status_code}")
        return False

def test_create_expense():
    print("\n💰 Testing expense creation...")
    
    # Test GET request to create page
    response = session.get(f'{base_url}/expenses/expenses/create')
    if response.status_code != 200:
        print(f"❌ Cannot access expense create page: {response.status_code}")
        return False
    
    # Test POST request to create an expense
    expense_data = {
        'title': 'Test Expense',
        'description': 'Test expense created by automated test',
        'amount': '50.00',
        'category': 'Office Supplies',
        'date': '2024-01-15'
    }
    
    response = session.post(f'{base_url}/expenses/expenses/create', data=expense_data)
    if response.status_code == 200 or (response.status_code == 302 and 'expenses' in response.headers.get('Location', '')):
        print("✅ Expense creation successful!")
        return True
    else:
        print(f"❌ Expense creation failed: {response.status_code}")
        return False

def test_work_timer():
    print("\n⏱️ Testing work timer...")
    
    response = session.get(f'{base_url}/work/timer')
    if response.status_code == 200:
        print("✅ Work timer page loads successfully!")
        return True
    else:
        print(f"❌ Work timer page failed: {response.status_code}")
        return False

def test_dashboard():
    print("\n📊 Testing dashboard...")
    
    response = session.get(f'{base_url}/dashboard')
    if response.status_code == 200:
        print("✅ Dashboard loads successfully!")
        return True
    else:
        print(f"❌ Dashboard failed: {response.status_code}")
        return False

def test_settings():
    print("\n⚙️ Testing settings...")
    
    response = session.get(f'{base_url}/settings')
    if response.status_code == 200:
        print("✅ Settings page loads successfully!")
        return True
    else:
        print(f"❌ Settings page failed: {response.status_code}")
        return False

def main():
    print("🧪 Smart Billing System - Comprehensive Functionality Test")
    print("=" * 60)
    
    tests = [
        test_login,
        test_dashboard,
        test_create_bill,
        test_view_bills,
        test_create_expense,
        test_work_timer,
        test_settings
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📈 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All functionality tests passed! The system is working correctly.")
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
