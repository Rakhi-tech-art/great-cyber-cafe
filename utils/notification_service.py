"""
Notification Service for Smart Billing System
Handles email and WhatsApp notifications based on user preferences
"""

from datetime import datetime, time
from flask import current_app
from models import NotificationPreferences
from utils.email_sender import send_email
from utils.whatsapp_sender import send_whatsapp_message

class NotificationService:
    """Service to handle all notifications based on user preferences"""
    
    @staticmethod
    def is_quiet_hours(user_prefs):
        """Check if current time is within user's quiet hours"""
        if not user_prefs or not user_prefs.quiet_hours_start or not user_prefs.quiet_hours_end:
            return False
        
        current_time = datetime.now().time()
        start_time = user_prefs.quiet_hours_start
        end_time = user_prefs.quiet_hours_end
        
        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if start_time > end_time:
            return current_time >= start_time or current_time <= end_time
        else:
            return start_time <= current_time <= end_time
    
    @staticmethod
    def send_bill_created_notification(user, bill):
        """Send notification when a new bill is created"""
        prefs = user.get_notification_preferences()
        
        if NotificationService.is_quiet_hours(prefs):
            return
        
        if prefs.email_bill_created:
            subject = f"New Invoice Created - #{bill.bill_number}"
            body = f"""
            Dear {user.username},
            
            A new invoice has been created in your Smart Billing System.
            
            Invoice Details:
            - Invoice Number: #{bill.bill_number}
            - Customer: {bill.customer.name}
            - Amount: Rs {bill.total_amount:.2f}
            - Status: {bill.status.title()}
            - Created: {bill.created_at.strftime('%Y-%m-%d %H:%M')}
            
            You can view the invoice details in your dashboard.
            
            Best regards,
            Smart Billing System
            """
            send_email(user.email, subject, body)
    
    @staticmethod
    def send_bill_paid_notification(user, bill):
        """Send notification when a bill is marked as paid"""
        prefs = user.get_notification_preferences()
        
        if NotificationService.is_quiet_hours(prefs):
            return
        
        if prefs.email_bill_paid:
            subject = f"Payment Received - Invoice #{bill.bill_number}"
            body = f"""
            Dear {user.username},
            
            Payment has been received for invoice #{bill.bill_number}.
            
            Payment Details:
            - Invoice Number: #{bill.bill_number}
            - Customer: {bill.customer.name}
            - Amount Paid: Rs {bill.total_amount:.2f}
            - Payment Date: {bill.paid_date.strftime('%Y-%m-%d %H:%M') if bill.paid_date else 'N/A'}
            
            Thank you for using Smart Billing System.
            
            Best regards,
            Smart Billing System
            """
            send_email(user.email, subject, body)
        
        if prefs.whatsapp_bill_paid and user.phone:
            message = f"""🧾 *Smart Billing Alert*

Payment received for Invoice #{bill.bill_number}
Customer: {bill.customer.name}
Amount: Rs {bill.total_amount:.2f}
Status: Paid ✅

Great Cyber Cafe"""
            send_whatsapp_message(user.phone, message)
    
    @staticmethod
    def send_expense_added_notification(user, expense):
        """Send notification when a new expense is added"""
        prefs = user.get_notification_preferences()
        
        if NotificationService.is_quiet_hours(prefs):
            return
        
        if prefs.email_expense_added:
            subject = f"New Expense Added - {expense.title}"
            body = f"""
            Dear {user.username},
            
            A new expense has been recorded in your Smart Billing System.
            
            Expense Details:
            - Title: {expense.title}
            - Category: {expense.category}
            - Amount: Rs {expense.amount:.2f}
            - Date: {expense.date.strftime('%Y-%m-%d')}
            - Description: {expense.description or 'N/A'}
            
            You can view all expenses in your expense tracker.
            
            Best regards,
            Smart Billing System
            """
            send_email(user.email, subject, body)
    
    @staticmethod
    def send_daily_summary(user, summary_data):
        """Send daily business summary via WhatsApp"""
        prefs = user.get_notification_preferences()
        
        if not prefs.whatsapp_daily_summary or not user.phone:
            return
        
        message = f"""📊 *Daily Business Summary*

Date: {datetime.now().strftime('%Y-%m-%d')}

💰 Revenue: Rs {summary_data.get('revenue', 0):.2f}
💸 Expenses: Rs {summary_data.get('expenses', 0):.2f}
📋 New Invoices: {summary_data.get('new_invoices', 0)}
✅ Payments: {summary_data.get('payments', 0)}

Great Cyber Cafe"""
        send_whatsapp_message(user.phone, message)
    
    @staticmethod
    def send_overdue_bills_alert(user, overdue_bills):
        """Send alert for overdue bills"""
        prefs = user.get_notification_preferences()
        
        if not prefs.whatsapp_overdue or not user.phone or not overdue_bills:
            return
        
        bill_list = "\n".join([f"#{bill.bill_number} - {bill.customer.name} - Rs {bill.total_amount:.2f}" 
                              for bill in overdue_bills[:5]])  # Limit to 5 bills
        
        message = f"""⚠️ *Overdue Bills Alert*

You have {len(overdue_bills)} overdue invoice(s):

{bill_list}

Please follow up with customers for payment.

Great Cyber Cafe"""
        send_whatsapp_message(user.phone, message)
    
    @staticmethod
    def send_goal_achievement_notification(user, goal_data):
        """Send notification when revenue goals are achieved"""
        prefs = user.get_notification_preferences()
        
        if not prefs.whatsapp_goals or not user.phone:
            return
        
        message = f"""🎉 *Goal Achievement!*

Congratulations! You've reached your {goal_data.get('period', 'monthly')} revenue goal.

Target: Rs {goal_data.get('target', 0):.2f}
Achieved: Rs {goal_data.get('achieved', 0):.2f}
Progress: {goal_data.get('percentage', 100):.1f}%

Keep up the great work!

Great Cyber Cafe"""
        send_whatsapp_message(user.phone, message)
