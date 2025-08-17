#!/usr/bin/env python3
"""
Test the role-based access control system
"""

from app import app
from models import db, User
from werkzeug.security import generate_password_hash

def test_role_system():
    """Test role-based functionality"""
    with app.app_context():
        # Check admin user
        admin = User.query.filter_by(email='admin@smartbilling.com').first()
        if admin:
            print(f"✅ Admin user found: {admin.username} (Role: {admin.role})")
            print(f"✅ Is admin: {admin.is_admin()}")
        else:
            print("❌ Admin user not found")
        
        # Create a test regular user
        test_user = User.query.filter_by(email='testuser@example.com').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='testuser@example.com',
                role='user',
                phone='1234567890'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            print("✅ Created test user")
        else:
            print("✅ Test user already exists")
        
        print(f"✅ Test user: {test_user.username} (Role: {test_user.role})")
        print(f"✅ Is admin: {test_user.is_admin()}")
        
        # Test notification preferences for both users
        admin_prefs = admin.get_notification_preferences()
        user_prefs = test_user.get_notification_preferences()
        
        print(f"✅ Admin notification preferences: {admin_prefs}")
        print(f"✅ User notification preferences: {user_prefs}")
        
        print("\n🎉 Role-based system test completed!")
        print("\nRole Summary:")
        print(f"- Admin ({admin.username}): Full access to all features")
        print(f"- User ({test_user.username}): Limited access to personal features")

if __name__ == '__main__':
    test_role_system()
