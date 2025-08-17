#!/usr/bin/env python3
"""
Smart Billing System Installation Script
This script sets up the database and creates initial data
"""

import os
import sys
from flask import Flask
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_app():
    """Create Flask app for installation"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'installation-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_billing.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    return app

def install_system():
    """Install the Smart Billing System"""
    print("🚀 Installing Smart Billing System...")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Import models
        from models import db, User, Customer, ExpenseCategory
        
        # Initialize database
        db.init_app(app)
        
        print("📦 Creating database tables...")
        db.create_all()
        
        # Create default admin user
        print("👤 Creating default admin user...")
        admin = User.query.filter_by(email='admin@smartbilling.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@smartbilling.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                phone='9004398030'
            )
            db.session.add(admin)
        
        # Create sample customer
        print("👥 Creating sample customer...")
        customer = Customer.query.filter_by(email='customer@example.com').first()
        if not customer:
            customer = Customer(
                name='Sample Customer',
                email='customer@example.com',
                phone='9876543210',
                whatsapp='9876543210',
                address='123 Sample Street, Sample City, 123456'
            )
            db.session.add(customer)
        
        # Create default expense categories
        print("📊 Creating expense categories...")
        default_categories = [
            ('Office Supplies', 'Stationery, equipment, and office materials'),
            ('Travel', 'Business travel and transportation expenses'),
            ('Meals', 'Business meals and entertainment'),
            ('Utilities', 'Electricity, internet, phone bills'),
            ('Software', 'Software licenses and subscriptions'),
            ('Marketing', 'Advertising and promotional expenses'),
            ('Equipment', 'Hardware and equipment purchases'),
            ('Rent', 'Office rent and facility costs'),
            ('Insurance', 'Business insurance premiums'),
            ('Other', 'Miscellaneous business expenses')
        ]
        
        for name, description in default_categories:
            category = ExpenseCategory.query.filter_by(name=name).first()
            if not category:
                category = ExpenseCategory(name=name, description=description)
                db.session.add(category)
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Installation completed successfully!")
        print("\n" + "=" * 50)
        print("🎉 Smart Billing System is ready to use!")
        print("\n📋 Default Login Credentials:")
        print("   Email: admin@smartbilling.com")
        print("   Password: admin123")
        print("\n🚀 To start the application, run:")
        print("   python app.py")
        print("\n🌐 Then open your browser and go to:")
        print("   http://localhost:5000")
        print("\n⚠️  Important: Change the default admin password after first login!")
        print("=" * 50)

if __name__ == '__main__':
    try:
        install_system()
    except Exception as e:
        print(f"❌ Installation failed: {str(e)}")
        print("Please check the error and try again.")
        sys.exit(1)
