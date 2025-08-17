from flask import Blueprint, render_template, redirect, url_for, send_file, make_response, jsonify
from flask_login import login_required, current_user
from models import Bill, Expense, WorkEntry, User, Customer, BillItem, db
from sqlalchemy import func
from datetime import datetime, timedelta
import csv
import io

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get current month data
    current_month = datetime.now().replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    today = datetime.now().date()

    # Role-based dashboard content
    if current_user.is_admin():
        return admin_dashboard(current_month, next_month, today)
    else:
        return user_dashboard(current_month, next_month, today)

def admin_dashboard(current_month, next_month, today):
    """Admin dashboard with full system statistics"""
    # Bills statistics (all users)
    total_bills = Bill.query.count()
    monthly_bills = Bill.query.filter(
        Bill.created_at >= current_month,
        Bill.created_at < next_month
    ).count()

    # Revenue statistics (all users)
    total_revenue = db.session.query(func.sum(Bill.total_amount)).filter(
        Bill.status == 'paid'
    ).scalar() or 0

    monthly_revenue = db.session.query(func.sum(Bill.total_amount)).filter(
        Bill.status == 'paid',
        Bill.created_at >= current_month,
        Bill.created_at < next_month
    ).scalar() or 0

    # Expense statistics (all users)
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    monthly_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.date >= current_month,
        Expense.date < next_month
    ).scalar() or 0

    # Remaining amount statistics (all users)
    total_remaining = db.session.query(func.sum(Bill.remaining_amount)).scalar() or 0
    monthly_remaining = db.session.query(func.sum(Bill.remaining_amount)).filter(
        Bill.created_at >= current_month,
        Bill.created_at < next_month
    ).scalar() or 0

    # Work Entry statistics (all users)
    from models import WorkEntry
    total_work_entries = WorkEntry.query.count()
    monthly_work_entries = WorkEntry.query.filter(
        WorkEntry.created_at >= current_month,
        WorkEntry.created_at < next_month
    ).count()

    # Work status breakdown (all users)
    pending_work = WorkEntry.query.filter(
        WorkEntry.work_status == 'pending'
    ).count()
    in_progress_work = WorkEntry.query.filter(
        WorkEntry.work_status == 'in_progress'
    ).count()
    completed_work = WorkEntry.query.filter(
        WorkEntry.work_status == 'completed'
    ).count()
    delivered_work = WorkEntry.query.filter(
        WorkEntry.work_status == 'delivered'
    ).count()

    # Work revenue (all users)
    work_revenue = db.session.query(func.sum(WorkEntry.total_amount)).filter(
        WorkEntry.payment_status == 'paid'
    ).scalar() or 0
    monthly_work_revenue = db.session.query(func.sum(WorkEntry.total_amount)).filter(
        WorkEntry.payment_status == 'paid',
        WorkEntry.created_at >= current_month,
        WorkEntry.created_at < next_month
    ).scalar() or 0

    # Recent activities (all users)
    recent_bills = Bill.query.order_by(Bill.created_at.desc()).limit(5).all()
    recent_expenses = Expense.query.order_by(Expense.date.desc()).limit(5).all()
    recent_work = WorkEntry.query.order_by(WorkEntry.created_at.desc()).limit(5).all()

    # Profit calculation
    total_combined_revenue = total_revenue + work_revenue
    monthly_combined_revenue = monthly_revenue + monthly_work_revenue
    monthly_profit = monthly_combined_revenue - monthly_expenses
    total_profit = total_combined_revenue - total_expenses

    # Pending payments (bills + work entries) - all users
    pending_bill_payments = db.session.query(func.sum(Bill.remaining_amount)).filter(
        Bill.remaining_amount > 0
    ).scalar() or 0
    pending_work_payments = db.session.query(func.sum(WorkEntry.remaining_amount)).filter(
        WorkEntry.remaining_amount > 0
    ).scalar() or 0
    total_pending_payments = pending_bill_payments + pending_work_payments

    # Today's tasks (all users)
    today_work = WorkEntry.query.filter(
        WorkEntry.work_status.in_(['pending', 'in_progress']),
        func.date(WorkEntry.created_at) == today
    ).count()

    # Total users count
    total_users = User.query.count()

    stats = {
        'total_bills': total_bills,
        'monthly_bills': monthly_bills,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'total_expenses': total_expenses,
        'monthly_expenses': monthly_expenses,
        'total_remaining': total_remaining,
        'monthly_remaining': monthly_remaining,
        'monthly_profit': monthly_profit,
        'total_profit': total_profit,
        'recent_bills': recent_bills,
        'recent_expenses': recent_expenses,
        'recent_work': recent_work,
        'total_work_entries': total_work_entries,
        'monthly_work_entries': monthly_work_entries,
        'pending_work': pending_work,
        'in_progress_work': in_progress_work,
        'completed_work': completed_work,
        'delivered_work': delivered_work,
        'work_revenue': work_revenue,
        'monthly_work_revenue': monthly_work_revenue,
        'total_combined_revenue': total_combined_revenue,
        'monthly_combined_revenue': monthly_combined_revenue,
        'total_pending_payments': total_pending_payments,
        'today_work': today_work,
        'total_users': total_users,
        'is_admin': True
    }

    return render_template('dashboard.html', stats=stats)

def user_dashboard(current_month, next_month, today):
    """User dashboard with limited personal statistics"""
    # Bills statistics (user only)
    total_bills = Bill.query.filter_by(created_by=current_user.id).count()
    monthly_bills = Bill.query.filter(
        Bill.created_by == current_user.id,
        Bill.created_at >= current_month,
        Bill.created_at < next_month
    ).count()

    # Revenue statistics (user only)
    total_revenue = db.session.query(func.sum(Bill.total_amount)).filter(
        Bill.created_by == current_user.id,
        Bill.status == 'paid'
    ).scalar() or 0

    monthly_revenue = db.session.query(func.sum(Bill.total_amount)).filter(
        Bill.created_by == current_user.id,
        Bill.status == 'paid',
        Bill.created_at >= current_month,
        Bill.created_at < next_month
    ).scalar() or 0

    # Work Entry statistics (user only)
    from models import WorkEntry
    total_work_entries = WorkEntry.query.filter_by(user_id=current_user.id).count()
    monthly_work_entries = WorkEntry.query.filter(
        WorkEntry.user_id == current_user.id,
        WorkEntry.created_at >= current_month,
        WorkEntry.created_at < next_month
    ).count()

    # Work status breakdown (user only)
    pending_work = WorkEntry.query.filter(
        WorkEntry.user_id == current_user.id,
        WorkEntry.work_status == 'pending'
    ).count()
    in_progress_work = WorkEntry.query.filter(
        WorkEntry.user_id == current_user.id,
        WorkEntry.work_status == 'in_progress'
    ).count()
    completed_work = WorkEntry.query.filter(
        WorkEntry.user_id == current_user.id,
        WorkEntry.work_status == 'completed'
    ).count()

    # Work revenue (user only)
    work_revenue = db.session.query(func.sum(WorkEntry.total_amount)).filter(
        WorkEntry.user_id == current_user.id,
        WorkEntry.payment_status == 'paid'
    ).scalar() or 0
    monthly_work_revenue = db.session.query(func.sum(WorkEntry.total_amount)).filter(
        WorkEntry.user_id == current_user.id,
        WorkEntry.payment_status == 'paid',
        WorkEntry.created_at >= current_month,
        WorkEntry.created_at < next_month
    ).scalar() or 0

    # Recent activities (user only)
    recent_bills = Bill.query.filter_by(created_by=current_user.id).order_by(Bill.created_at.desc()).limit(5).all()
    recent_work = WorkEntry.query.filter_by(user_id=current_user.id).order_by(WorkEntry.created_at.desc()).limit(5).all()

    # Pending payments (user only)
    pending_bill_payments = db.session.query(func.sum(Bill.remaining_amount)).filter(
        Bill.created_by == current_user.id,
        Bill.remaining_amount > 0
    ).scalar() or 0
    pending_work_payments = db.session.query(func.sum(WorkEntry.remaining_amount)).filter(
        WorkEntry.user_id == current_user.id,
        WorkEntry.remaining_amount > 0
    ).scalar() or 0
    total_pending_payments = pending_bill_payments + pending_work_payments

    # Today's tasks (user only)
    today_work = WorkEntry.query.filter(
        WorkEntry.user_id == current_user.id,
        WorkEntry.work_status.in_(['pending', 'in_progress']),
        func.date(WorkEntry.created_at) == today
    ).count()

    # Combined revenue
    total_combined_revenue = total_revenue + work_revenue
    monthly_combined_revenue = monthly_revenue + monthly_work_revenue

    stats = {
        'total_bills': total_bills,
        'monthly_bills': monthly_bills,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'recent_bills': recent_bills,
        'recent_work': recent_work,
        'total_work_entries': total_work_entries,
        'monthly_work_entries': monthly_work_entries,
        'pending_work': pending_work,
        'in_progress_work': in_progress_work,
        'completed_work': completed_work,
        'work_revenue': work_revenue,
        'monthly_work_revenue': monthly_work_revenue,
        'total_combined_revenue': total_combined_revenue,
        'monthly_combined_revenue': monthly_combined_revenue,
        'total_pending_payments': total_pending_payments,
        'today_work': today_work,
        'is_admin': False
    }

    return render_template('dashboard.html', stats=stats)

@main_bp.route('/export/<data_type>')
@login_required
def export_data(data_type):
    """Export data as CSV file"""
    try:
        # Validate data type
        valid_types = ['bills', 'expenses', 'work', 'all']
        if data_type not in valid_types:
            return f"Invalid data type. Valid types: {', '.join(valid_types)}", 400

        # Route to appropriate export function
        if data_type == 'bills':
            return export_bills_data()
        elif data_type == 'expenses':
            return export_expenses_data()
        elif data_type == 'work':
            return export_work_data()
        elif data_type == 'all':
            return export_all_data()

    except Exception as e:
        # Log the error for debugging
        print(f"Export error for {data_type}: {str(e)}")
        return f"Export failed: {str(e)}", 500

def export_bills_data():
    """Export bills data to CSV"""
    # Get bills for current user
    bills = Bill.query.filter_by(created_by=current_user.id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Bill Number', 'Customer Name', 'Customer Email', 'Customer Phone',
        'Total Amount', 'Advance Amount', 'Remaining Amount', 'Status',
        'Created Date', 'Due Date', 'Paid Date', 'Items', 'Notes'
    ])

    # Write data
    for bill in bills:
        # Get bill items
        items_text = '; '.join([f"{item.description} (Qty: {item.quantity}, Rate: Rs {item.rate})"
                               for item in bill.items])

        writer.writerow([
            bill.bill_number,
            bill.customer.name,
            bill.customer.email or '',
            bill.customer.phone or '',
            f"Rs {bill.total_amount:.2f}",
            f"Rs {bill.advance_amount:.2f}",
            f"Rs {bill.remaining_amount:.2f}",
            bill.status.title(),
            bill.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            bill.due_date.strftime('%Y-%m-%d') if bill.due_date else '',
            bill.paid_date.strftime('%Y-%m-%d %H:%M:%S') if bill.paid_date else '',
            items_text,
            bill.notes or ''
        ])

    output.seek(0)

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=bills_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

def export_expenses_data():
    """Export expenses data to CSV"""
    # Get expenses for current user
    expenses = Expense.query.filter_by(created_by=current_user.id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Date', 'Description', 'Category', 'Amount', 'Payment Method',
        'Receipt Number', 'Notes', 'Created Date'
    ])

    # Write data
    for expense in expenses:
        writer.writerow([
            expense.date.strftime('%Y-%m-%d'),
            expense.description,
            expense.category or '',
            f"Rs {expense.amount:.2f}",
            expense.payment_method or '',
            expense.receipt_number or '',
            expense.notes or '',
            expense.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    output.seek(0)

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=expenses_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

def export_work_data():
    """Export work entries data to CSV"""
    # Get work entries for current user
    work_entries = WorkEntry.query.filter_by(user_id=current_user.id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Project Name', 'Customer Name', 'Customer Phone', 'Service Type',
        'Start Time', 'End Time', 'Duration (Hours)', 'Hourly Rate',
        'Total Amount', 'Advance Amount', 'Remaining Amount',
        'Work Status', 'Payment Status', 'Created Date'
    ])

    # Write data
    for entry in work_entries:
        duration_hours = (entry.duration_minutes / 60) if entry.duration_minutes else 0

        writer.writerow([
            entry.project_name or '',
            entry.customer_name or '',
            entry.customer_phone or '',
            entry.service_type or '',
            entry.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            entry.end_time.strftime('%Y-%m-%d %H:%M:%S') if entry.end_time else '',
            f"{duration_hours:.2f}",
            f"Rs {entry.hourly_rate:.2f}",
            f"Rs {entry.total_amount:.2f}",
            f"Rs {entry.advance_amount:.2f}",
            f"Rs {entry.remaining_amount:.2f}",
            entry.work_status.title(),
            entry.payment_status.title(),
            entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    output.seek(0)

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=work_entries_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

def export_all_data():
    """Export all data in a comprehensive CSV file"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write summary header
    writer.writerow(['SMART BILLING SYSTEM - COMPLETE DATA EXPORT'])
    writer.writerow([f'Export Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
    writer.writerow([f'User: {current_user.username}'])
    writer.writerow([''])

    # BILLS SECTION
    writer.writerow(['=== BILLS DATA ==='])
    writer.writerow([
        'Bill Number', 'Customer Name', 'Customer Email', 'Customer Phone',
        'Total Amount', 'Advance Amount', 'Remaining Amount', 'Status',
        'Created Date', 'Items Count', 'Notes'
    ])

    bills = Bill.query.filter_by(created_by=current_user.id).all()
    for bill in bills:
        writer.writerow([
            bill.bill_number,
            bill.customer.name,
            bill.customer.email or '',
            bill.customer.phone or '',
            f"Rs {bill.total_amount:.2f}",
            f"Rs {bill.advance_amount:.2f}",
            f"Rs {bill.remaining_amount:.2f}",
            bill.status.title(),
            bill.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            len(bill.items),
            bill.notes or ''
        ])

    writer.writerow([''])

    # EXPENSES SECTION
    writer.writerow(['=== EXPENSES DATA ==='])
    writer.writerow([
        'Date', 'Description', 'Category', 'Amount', 'Payment Method', 'Notes'
    ])

    expenses = Expense.query.filter_by(created_by=current_user.id).all()
    for expense in expenses:
        writer.writerow([
            expense.date.strftime('%Y-%m-%d'),
            expense.description,
            expense.category or '',
            f"Rs {expense.amount:.2f}",
            expense.payment_method or '',
            expense.notes or ''
        ])

    writer.writerow([''])

    # WORK ENTRIES SECTION
    writer.writerow(['=== WORK ENTRIES DATA ==='])
    writer.writerow([
        'Project Name', 'Customer Name', 'Service Type', 'Duration (Hours)',
        'Total Amount', 'Work Status', 'Payment Status', 'Start Time'
    ])

    work_entries = WorkEntry.query.filter_by(user_id=current_user.id).all()
    for entry in work_entries:
        duration_hours = (entry.duration_minutes / 60) if entry.duration_minutes else 0
        writer.writerow([
            entry.project_name or '',
            entry.customer_name or '',
            entry.service_type or '',
            f"{duration_hours:.2f}",
            f"Rs {entry.total_amount:.2f}",
            entry.work_status.title(),
            entry.payment_status.title(),
            entry.start_time.strftime('%Y-%m-%d %H:%M:%S')
        ])

    writer.writerow([''])

    # SUMMARY SECTION
    writer.writerow(['=== SUMMARY ==='])
    total_bills = len(bills)
    total_revenue = sum(bill.total_amount for bill in bills)
    total_expenses_amount = sum(expense.amount for expense in expenses)
    total_work_entries = len(work_entries)
    total_work_amount = sum(entry.total_amount for entry in work_entries)

    writer.writerow(['Total Bills:', total_bills])
    writer.writerow(['Total Revenue:', f"Rs {total_revenue:.2f}"])
    writer.writerow(['Total Expenses:', f"Rs {total_expenses_amount:.2f}"])
    writer.writerow(['Total Work Entries:', total_work_entries])
    writer.writerow(['Total Work Amount:', f"Rs {total_work_amount:.2f}"])
    writer.writerow(['Net Profit:', f"Rs {(total_revenue - total_expenses_amount):.2f}"])

    output.seek(0)

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=complete_data_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

@main_bp.route('/export/stats')
@login_required
def export_stats():
    """Get export statistics for the current user"""
    try:
        # Count records for each data type
        bills_count = Bill.query.filter_by(created_by=current_user.id).count()
        expenses_count = Expense.query.filter_by(created_by=current_user.id).count()
        work_count = WorkEntry.query.filter_by(user_id=current_user.id).count()

        # Calculate totals
        total_revenue = db.session.query(func.sum(Bill.total_amount)).filter_by(created_by=current_user.id).scalar() or 0
        total_expenses = db.session.query(func.sum(Expense.amount)).filter_by(created_by=current_user.id).scalar() or 0
        total_work_amount = db.session.query(func.sum(WorkEntry.total_amount)).filter_by(user_id=current_user.id).scalar() or 0

        stats = {
            'bills': {
                'count': bills_count,
                'total_amount': float(total_revenue)
            },
            'expenses': {
                'count': expenses_count,
                'total_amount': float(total_expenses)
            },
            'work': {
                'count': work_count,
                'total_amount': float(total_work_amount)
            },
            'summary': {
                'total_records': bills_count + expenses_count + work_count,
                'net_profit': float(total_revenue - total_expenses)
            }
        }

        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
