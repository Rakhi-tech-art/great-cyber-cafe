import requests
import sys

base_url = 'http://localhost:5000'
pages_to_test = [
    '/',
    '/auth/login',
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

print('Testing all pages...')
print('=' * 50)

for page in pages_to_test:
    try:
        response = requests.get(base_url + page, allow_redirects=False)
        status = response.status_code
        if status == 200:
            print(f'OK {page} - {status}')
        elif status == 302:
            print(f'REDIRECT {page} - {status} (probably needs login)')
        else:
            print(f'ERROR {page} - {status}')
    except Exception as e:
        print(f'EXCEPTION {page} - {str(e)}')

print('=' * 50)
print('Testing complete!')
