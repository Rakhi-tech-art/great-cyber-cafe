import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from flask import current_app

def send_bill_email(bill, pdf_path):
    """Send bill via email with PDF attachment"""

    # Validate email address
    if not bill.customer.email:
        raise ValueError("Customer email address is not provided")

    # Email configuration
    smtp_server = current_app.config['MAIL_SERVER']
    smtp_port = current_app.config['MAIL_PORT']
    sender_email = current_app.config['MAIL_USERNAME']
    sender_password = current_app.config['MAIL_PASSWORD']

    if not all([smtp_server, smtp_port, sender_email, sender_password]):
        raise ValueError("Email configuration is incomplete")

    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = bill.customer.email
    msg['Subject'] = f"Invoice {bill.bill_number} - Smart Billing System"
    
    # Email body
    body = f"""Dear {bill.customer.name},

Thank you for your support! Please find attached your invoice {bill.bill_number}.

Invoice Details:
- Invoice Number: {bill.bill_number}
- Date: {bill.created_at.strftime('%d/%m/%Y')}
- Amount: Rs {bill.total_amount:.2f}

If you have any questions about this invoice, please contact us at:
Email: greatcybercafe852@gmail.com
Phone: 9004398030

Best regards,
Great Cyber Cafe"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach PDF
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {bill.bill_number}.pdf'
        )
        msg.attach(part)
    
    # Send email
    server = None
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, bill.customer.email, text)
        return True
    except smtplib.SMTPAuthenticationError:
        raise Exception("Email authentication failed. Please check your email credentials.")
    except smtplib.SMTPRecipientsRefused:
        raise Exception(f"Invalid recipient email address: {bill.customer.email}")
    except smtplib.SMTPServerDisconnected:
        raise Exception("Email server connection lost. Please try again.")
    except Exception as e:
        raise Exception(f"Email sending failed: {str(e)}")
    finally:
        if server:
            try:
                server.quit()
            except:
                pass

def send_notification_email(to_email, subject, body):
    """Send general notification email"""
    
    # Email configuration
    smtp_server = current_app.config['MAIL_SERVER']
    smtp_port = current_app.config['MAIL_PORT']
    sender_email = current_app.config['MAIL_USERNAME']
    sender_password = current_app.config['MAIL_PASSWORD']
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        raise e
