#!/usr/bin/env python3
"""
Deployment Check Script
Verifies that the application can start correctly in a production environment
"""

import os
import sys
from datetime import datetime

def check_environment():
    """Check environment variables and configuration"""
    print("🔍 Checking Environment Configuration...")
    print("-" * 50)
    
    # Check Python version
    python_version = sys.version
    print(f"Python Version: {python_version}")
    
    # Check critical environment variables
    env_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'WHATSAPP_NUMBER'
    ]
    
    missing_vars = []
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'PASSWORD' in var or 'SECRET' in var:
                display_value = '*' * len(value)
            else:
                display_value = value
            print(f"✓ {var}: {display_value}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("These will use default values from .env file or hardcoded defaults")
    
    return len(missing_vars) == 0

def check_dependencies():
    """Check if all required dependencies can be imported"""
    print("\n📦 Checking Dependencies...")
    print("-" * 50)
    
    dependencies = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('flask_login', 'Flask-Login'),
        ('flask_wtf', 'Flask-WTF'),
        ('flask_mail', 'Flask-Mail'),
        ('wtforms', 'WTForms'),
        ('werkzeug', 'Werkzeug'),
        ('reportlab', 'ReportLab'),

        ('dotenv', 'python-dotenv'),
        ('requests', 'requests'),
        ('pywhatkit', 'pywhatkit'),

        ('email_validator', 'email-validator'),
        ('bcrypt', 'bcrypt'),
        ('gunicorn', 'gunicorn'),
        ('psycopg2', 'psycopg2-binary')
    ]
    
    failed_imports = []
    
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {package_name}")
        except ImportError as e:
            failed_imports.append((package_name, str(e)))
            print(f"❌ {package_name}: {e}")
    
    return len(failed_imports) == 0, failed_imports

def check_app_startup():
    """Check if the Flask app can start"""
    print("\n🚀 Checking Application Startup...")
    print("-" * 50)
    
    try:
        # Import the app
        from app import app
        
        # Test app context
        with app.app_context():
            print("✓ Flask app created successfully")
            print("✓ App context works")
            
            # Check database connection
            from models import db
            try:
                # Try to create tables (this will test DB connection)
                db.create_all()
                print("✓ Database connection successful")
                print("✓ Database tables created/verified")
            except Exception as e:
                print(f"❌ Database error: {e}")
                return False
            
        return True
        
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False

def main():
    """Main deployment check function"""
    print("🔧 Smart Billing System - Deployment Check")
    print("=" * 60)
    print(f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run all checks
    env_ok = check_environment()
    deps_ok, failed_deps = check_dependencies()
    app_ok = check_app_startup()
    
    # Summary
    print("\n📋 Deployment Check Summary")
    print("=" * 60)
    
    if env_ok and deps_ok and app_ok:
        print("🎉 All checks passed! Application is ready for deployment.")
        return 0
    else:
        print("❌ Some checks failed:")
        if not env_ok:
            print("   - Environment configuration issues")
        if not deps_ok:
            print("   - Dependency import issues:")
            for pkg, error in failed_deps:
                print(f"     * {pkg}: {error}")
        if not app_ok:
            print("   - Application startup issues")
        
        print("\n💡 Recommendations:")
        print("   1. Install missing dependencies: pip install -r requirements.txt")
        print("   2. Set missing environment variables")
        print("   3. Check database configuration")
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
