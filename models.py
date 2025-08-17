from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    phone = db.Column(db.String(15))
    profile_photo = db.Column(db.String(200))  # Path to profile photo
    theme = db.Column(db.String(10), default='light')  # 'light' or 'dark'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    bills = db.relationship('Bill', backref='created_by_user', lazy=True)
    expenses = db.relationship('Expense', backref='created_by_user', lazy=True)
    work_entries = db.relationship('WorkEntry', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_admin(self):
        return self.role == 'admin'

    def get_notification_preferences(self):
        """Get or create notification preferences for this user"""
        if not self.notification_preferences:
            prefs = NotificationPreferences(user_id=self.id)
            db.session.add(prefs)
            db.session.commit()
            return prefs
        return self.notification_preferences

    def __repr__(self):
        return f'<User {self.username}>'

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    whatsapp = db.Column(db.String(15))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bills = db.relationship('Bill', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Bill details
    subtotal = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    advance_amount = db.Column(db.Float, default=0.0)
    remaining_amount = db.Column(db.Float, default=0.0)
    
    # Status and dates
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    paid_date = db.Column(db.DateTime)
    
    # Communication
    email_sent = db.Column(db.Boolean, default=False)
    whatsapp_sent = db.Column(db.Boolean, default=False)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Relationships
    items = db.relationship('BillItem', backref='bill', lazy=True, cascade='all, delete-orphan')
    
    def calculate_totals(self):
        self.subtotal = sum(item.total for item in self.items)
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total_amount = self.subtotal + self.tax_amount - self.discount
        self.remaining_amount = max(0, self.total_amount - self.advance_amount)
    
    def __repr__(self):
        return f'<Bill {self.bill_number}>'

class BillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, default=1.0)
    rate = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<BillItem {self.description}>'

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receipt_path = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Expense {self.title}>'

class WorkEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Customer Information
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(15), nullable=False)

    # Service Information
    service_type = db.Column(db.String(50), nullable=False)  # passport, aadhaar, pan, etc.
    project_name = db.Column(db.String(100), nullable=False)
    task_description = db.Column(db.Text, nullable=False)

    # Time and Billing
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    hourly_rate = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    advance_amount = db.Column(db.Float, default=0.0)
    remaining_amount = db.Column(db.Float, default=0.0)

    # Status
    work_status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, delivered
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_duration(self):
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
            self.total_amount = (self.duration_minutes / 60) * self.hourly_rate
            self.remaining_amount = max(0, self.total_amount - self.advance_amount)

            # Update payment status based on amounts
            if self.remaining_amount == 0:
                self.payment_status = 'paid'
            elif self.advance_amount > 0:
                self.payment_status = 'partial'
            else:
                self.payment_status = 'pending'
    
    def __repr__(self):
        return f'<WorkEntry {self.project_name}>'

class ExpenseCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ExpenseCategory {self.name}>'

class NotificationPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    # Email Notifications
    email_bill_created = db.Column(db.Boolean, default=True)
    email_bill_paid = db.Column(db.Boolean, default=True)
    email_expense_added = db.Column(db.Boolean, default=False)
    email_weekly_report = db.Column(db.Boolean, default=True)
    email_monthly_report = db.Column(db.Boolean, default=True)
    email_system_updates = db.Column(db.Boolean, default=True)

    # WhatsApp Notifications
    whatsapp_bill_paid = db.Column(db.Boolean, default=False)
    whatsapp_daily_summary = db.Column(db.Boolean, default=False)
    whatsapp_overdue = db.Column(db.Boolean, default=False)
    whatsapp_goals = db.Column(db.Boolean, default=False)

    # Notification Schedule
    quiet_hours_start = db.Column(db.Time, default=datetime.strptime('22:00', '%H:%M').time())
    quiet_hours_end = db.Column(db.Time, default=datetime.strptime('08:00', '%H:%M').time())
    weekly_report_day = db.Column(db.String(10), default='monday')
    report_time = db.Column(db.Time, default=datetime.strptime('09:00', '%H:%M').time())

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref=db.backref('notification_preferences', uselist=False))

    def __repr__(self):
        return f'<NotificationPreferences for User {self.user_id}>'
