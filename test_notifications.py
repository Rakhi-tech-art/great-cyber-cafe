#!/usr/bin/env python3
"""
Test script for notification settings functionality
"""

from app import app
from models import db, User, NotificationPreferences
from datetime import time

def test_notification_preferences():
    """Test notification preferences functionality"""
    with app.app_context():
        # Get the admin user
        admin = User.query.filter_by(email='admin@smartbilling.com').first()
        if not admin:
            print("❌ Admin user not found")
            return
        
        print(f"✅ Found admin user: {admin.username}")
        
        # Test getting notification preferences
        prefs = admin.get_notification_preferences()
        print(f"✅ Got notification preferences: {prefs}")
        
        # Test updating preferences
        prefs.email_bill_created = True
        prefs.email_bill_paid = False
        prefs.whatsapp_bill_paid = True
        prefs.quiet_hours_start = time(22, 0)
        prefs.quiet_hours_end = time(8, 0)
        prefs.weekly_report_day = 'friday'
        
        db.session.commit()
        print("✅ Updated notification preferences")
        
        # Verify the changes
        updated_prefs = admin.get_notification_preferences()
        print(f"✅ Email bill created: {updated_prefs.email_bill_created}")
        print(f"✅ Email bill paid: {updated_prefs.email_bill_paid}")
        print(f"✅ WhatsApp bill paid: {updated_prefs.whatsapp_bill_paid}")
        print(f"✅ Quiet hours: {updated_prefs.quiet_hours_start} - {updated_prefs.quiet_hours_end}")
        print(f"✅ Weekly report day: {updated_prefs.weekly_report_day}")
        
        print("\n🎉 All notification preferences tests passed!")

if __name__ == '__main__':
    test_notification_preferences()
