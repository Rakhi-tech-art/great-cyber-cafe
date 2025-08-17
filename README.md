# Smart Billing System

A comprehensive web-based billing system built with Flask, SQLite, and Python. Features include billing management, work tracking, expense tracking, analytics, and automated email/WhatsApp notifications.

## Features

### 🧾 Billing System
- Create, edit, and manage bills
- PDF generation for invoices
- Email and WhatsApp integration for bill delivery
- Customer management
- Multiple bill statuses (draft, sent, paid, cancelled)

### ⏰ Work Tracker
- Time tracking for projects and tasks
- Hourly rate calculation
- Work entry management
- Project-based reporting

### 💰 Expense Tracker
- Record and categorize expenses
- Expense reporting and analytics
- Category-wise expense breakdown

### 📊 Dashboard & Analytics
- Profit/Loss analysis
- Revenue and expense charts
- Monthly and yearly reports
- Business performance metrics

### 👥 User Management
- Role-based access control (Admin/User)
- User registration and management
- Profile management

### 📧 Communication
- SMTP email integration
- WhatsApp message automation
- PDF bill attachments

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Quick Setup

1. **Clone or download the project**
   ```bash
   cd pro_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the installation script**
   ```bash
   python install.py
   ```

4. **Start the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to: `http://localhost:5000`

### Default Login
- **Email:** admin@smartbilling.com
- **Password:** admin123

⚠️ **Important:** Change the default password after first login!

## Configuration

### Email Settings
Update the email configuration in `.env` file:
```
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### WhatsApp Settings
Update the WhatsApp number in `.env` file:
```
WHATSAPP_NUMBER=your-whatsapp-number
```

## Project Structure

```
pro_app/
├── app.py                 # Main application file
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── install.py            # Installation script
├── .env                  # Environment variables
├── routes/               # Route handlers
│   ├── auth.py          # Authentication routes
│   ├── billing.py       # Billing system routes
│   ├── work_tracker.py  # Work tracking routes
│   ├── expense_tracker.py # Expense tracking routes
│   ├── dashboard.py     # Dashboard and analytics
│   └── main.py          # Main routes
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── dashboard.html  # Dashboard
│   ├── auth/           # Authentication templates
│   └── billing/        # Billing templates
├── static/             # Static files
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   └── images/        # Images
└── utils/              # Utility functions
    ├── pdf_generator.py # PDF generation
    ├── email_sender.py  # Email functionality
    └── whatsapp_sender.py # WhatsApp integration
```

## Usage

### Creating Bills
1. Navigate to **Billing** → **Create Bill**
2. Fill in customer information
3. Add bill items with quantities and rates
4. Set tax rate and discount if applicable
5. Save the bill
6. Send via email/WhatsApp or download PDF

### Work Tracking
1. Go to **Work Tracker** → **Create Entry**
2. Start a timer or manually enter work hours
3. Specify project name and task description
4. Set hourly rate for automatic calculation
5. Stop timer when work is complete

### Expense Management
1. Navigate to **Expense Tracker** → **Add Expense**
2. Enter expense details and category
3. Upload receipts if needed
4. View reports and analytics

### Analytics
1. Visit **Dashboard** for overview
2. Go to **Analytics** for detailed reports
3. Use filters to analyze specific periods
4. View profit/loss statements

## User Roles

### Admin
- Full access to all features
- User management capabilities
- System-wide analytics
- All billing and expense operations

### User
- Limited access to own data
- Can create bills and track work
- Can manage own expenses
- View personal analytics

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control
- CSRF protection with Flask-WTF
- Input validation and sanitization

## Email Configuration

For Gmail SMTP:
1. Enable 2-factor authentication
2. Generate an app-specific password
3. Use the app password in configuration

## WhatsApp Integration

The system uses `pywhatkit` for WhatsApp automation:
- Requires WhatsApp Web to be logged in
- Messages are sent through browser automation
- Ensure stable internet connection

## Troubleshooting

### Common Issues

1. **Database errors**
   - Run `python install.py` to recreate database

2. **Email not sending**
   - Check SMTP credentials
   - Verify app password for Gmail

3. **WhatsApp not working**
   - Ensure WhatsApp Web is logged in
   - Check phone number format (+91xxxxxxxxxx)

4. **PDF generation issues**
   - Verify reportlab installation
   - Check file permissions

## Support

For issues and questions:
- Email: greatcybercafe@gmail.com
- Phone: 9004398030

## License

This project is for educational and business use. Modify as needed for your requirements.

---

**Smart Billing System** - Streamline your business operations with automated billing, tracking, and analytics.
