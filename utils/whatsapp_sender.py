import os
from datetime import datetime, timedelta

# Try to import pywhatkit, but make it optional for deployment
try:
    import pywhatkit as pwk
    PYWHATKIT_AVAILABLE = True
except (ImportError, KeyError) as e:
    # KeyError occurs when DISPLAY environment variable is missing (headless servers)
    PYWHATKIT_AVAILABLE = False
    pwk = None
from flask import current_app

def send_whatsapp_message(bill, pdf_path=None):
    """Send WhatsApp message with bill details"""

    # Check if WhatsApp functionality is available
    if not PYWHATKIT_AVAILABLE:
        raise ValueError("WhatsApp functionality is not available in this environment (pywhatkit not installed or no display)")

    # Validate WhatsApp number
    if not bill.customer.whatsapp:
        raise ValueError("Customer WhatsApp number is not provided")

    # Format phone number (ensure it starts with country code)
    phone_number = bill.customer.whatsapp.strip()

    # Remove any non-digit characters except +
    import re
    phone_number = re.sub(r'[^\d+]', '', phone_number)

    if not phone_number.startswith('+'):
        # Assume Indian number if no country code
        phone_number = '+91' + phone_number.lstrip('0')

    # Validate phone number format
    if not re.match(r'^\+\d{10,15}$', phone_number):
        raise ValueError(f"Invalid WhatsApp number format: {phone_number}")
    
    # Create detailed message as requested
    message = f"""🧾 *Invoice from Great cyber cafe*

Dear {bill.customer.name},

Your invoice is ready!

📋 *Invoice Details:*
• Invoice Number: {bill.bill_number}
• Date: {bill.created_at.strftime('%d/%m/%Y')}
• Paid amount: Rs {bill.advance_amount:.2f}
• Remaining amount: Rs {bill.remaining_amount:.2f}
• Total amount: Rs {bill.total_amount:.2f}

💼 *Items:*"""

    # Add items
    for item in bill.items:
        message += f"\n• {item.description}: {item.quantity} × Rs {item.rate:.2f} = Rs {item.total:.2f}"

    message += f"""

💰 *Summary:*
• Subtotal: Rs {bill.subtotal:.2f}
• Paid amount: Rs {bill.advance_amount:.2f}
• Remaining amount: Rs {bill.remaining_amount:.2f}
• *Total: Rs {bill.total_amount:.2f}*

📞 For any queries, contact us:
Email: {current_app.config['MAIL_USERNAME']}
Phone: {current_app.config['WHATSAPP_NUMBER']}

Thank you for your business! 🙏

*Great Cyber Cafe*"""
    
    try:
        # Send message with proper timing
        now = datetime.now()
        send_time = now + timedelta(minutes=2)  # Send 2 minutes from now for better timing

        # Validate time (WhatsApp Web needs to be open during business hours)
        if send_time.hour < 6 or send_time.hour > 23:
            raise Exception("WhatsApp messages can only be sent between 6 AM and 11 PM")

        pwk.sendwhatmsg(
            phone_number,
            message,
            send_time.hour,
            send_time.minute,
            wait_time=20,  # Increased wait time
            tab_close=True
        )

        return True

    except Exception as e:
        error_msg = str(e).lower()
        if "selenium" in error_msg or "webdriver" in error_msg:
            raise Exception("WhatsApp Web is not accessible. Please ensure your browser supports WhatsApp Web.")
        elif "invalid" in error_msg and "number" in error_msg:
            raise Exception(f"Invalid WhatsApp number: {phone_number}")
        elif "network" in error_msg or "connection" in error_msg:
            raise Exception("Network connection error. Please check your internet connection.")
        else:
            raise Exception(f"WhatsApp sending failed: {str(e)}")

def send_whatsapp_notification(phone_number, message):
    """Send general WhatsApp notification"""
    
    # Format phone number
    if not phone_number.startswith('+'):
        phone_number = '+91' + phone_number.lstrip('0')
    
    try:
        now = datetime.now()
        send_time = now + timedelta(minutes=1)
        
        pwk.sendwhatmsg(
            phone_number,
            message,
            send_time.hour,
            send_time.minute,
            wait_time=15,
            tab_close=True
        )
        
        return True
        
    except Exception as e:
        print(f"WhatsApp sending failed: {str(e)}")
        raise e
