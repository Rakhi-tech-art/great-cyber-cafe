#!/usr/bin/env python3
"""
Migration script to add NotificationPreferences table
"""

from app import app
from models import db, NotificationPreferences

def migrate():
    """Create the notification preferences table"""
    with app.app_context():
        try:
            # Create the table
            db.create_all()
            print("✅ NotificationPreferences table created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating table: {e}")

if __name__ == '__main__':
    migrate()
