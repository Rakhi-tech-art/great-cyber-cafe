import requests
import sys

base_url = 'http://localhost:5000'

# Create a session to maintain cookies
session = requests.Session()

# Login first
login_data = {
    'email': 'admin@smartbilling.com',
    'password': 'admin123'
}

print('Logging in...')
login_response = session.post(f'{base_url}/auth/login', data=login_data)
if login_response.status_code == 200 and 'dashboard' in login_response.url:
    print('✅ Login successful!')
else:
    print(f'❌ Login failed: {login_response.status_code}')
    sys.exit(1)

# Pages to test after login
pages_to_test = [
    '/dashboard',
    '/billing/bills',
    '/billing/bills/create',
    '/billing/today',
    '/billing/last-week',
    '/billing/all',
    '/expenses/expenses',
    '/expenses/expenses/create',
    '/work/entries',
    '/work/entries/create',
    '/work/timer',
    '/dashboard/analytics',
    '/settings',
    '/auth/profile'
]

print('\nTesting authenticated pages...')
print('=' * 50)

for page in pages_to_test:
    try:
        response = session.get(base_url + page, allow_redirects=True)
        status = response.status_code
        if status == 200:
            # Check if page contains error indicators
            content = response.text.lower()
            if 'error' in content and 'template' in content:
                print(f'⚠️  {page} - Template Error')
            elif 'internal server error' in content:
                print(f'❌ {page} - Server Error')
            else:
                print(f'✅ {page} - OK')
        else:
            print(f'❌ {page} - Error {status}')
    except Exception as e:
        print(f'💥 {page} - Exception: {str(e)}')

print('=' * 50)
print('Testing complete!')
