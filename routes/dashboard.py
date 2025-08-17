from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Bill, Expense, WorkEntry, User, db
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from routes.auth import admin_required
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    # Get date range from query parameters
    period = request.args.get('period', '12months')  # 12months, 6months, 3months, 1month
    
    # Calculate date range
    end_date = datetime.now()
    if period == '1month':
        start_date = end_date - timedelta(days=30)
    elif period == '3months':
        start_date = end_date - timedelta(days=90)
    elif period == '6months':
        start_date = end_date - timedelta(days=180)
    else:  # 12months
        start_date = end_date - timedelta(days=365)
    
    # Revenue data (from paid bills) - SQLite compatible
    revenue_query = db.session.query(
        func.strftime('%Y-%m', Bill.created_at).label('month'),
        func.sum(Bill.total_amount).label('total')
    ).filter(
        Bill.status == 'paid',
        Bill.created_at >= start_date
    ).group_by(func.strftime('%Y-%m', Bill.created_at))
    
    if not current_user.is_admin():
        revenue_query = revenue_query.filter(Bill.created_by == current_user.id)
    
    revenue_data = revenue_query.all()
    
    # Expense data - SQLite compatible
    expense_query = db.session.query(
        func.strftime('%Y-%m', Expense.date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.date >= start_date
    ).group_by(func.strftime('%Y-%m', Expense.date))
    
    if not current_user.is_admin():
        expense_query = expense_query.filter(Expense.created_by == current_user.id)
    
    expense_data = expense_query.all()
    
    # Work hours data - SQLite compatible
    work_query = db.session.query(
        func.strftime('%Y-%m', WorkEntry.start_time).label('month'),
        func.sum(WorkEntry.duration_minutes).label('total_minutes')
    ).filter(
        WorkEntry.work_status == 'completed',
        WorkEntry.start_time >= start_date
    ).group_by(func.strftime('%Y-%m', WorkEntry.start_time))
    
    if not current_user.is_admin():
        work_query = work_query.filter(WorkEntry.user_id == current_user.id)
    
    work_data = work_query.all()
    
    # Category-wise expense breakdown
    category_query = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.date >= start_date
    ).group_by(Expense.category)
    
    if not current_user.is_admin():
        category_query = category_query.filter(Expense.created_by == current_user.id)
    
    category_data = category_query.all()
    
    # Bill status breakdown
    status_query = db.session.query(
        Bill.status,
        func.count(Bill.id).label('count'),
        func.sum(Bill.total_amount).label('total')
    ).filter(
        Bill.created_at >= start_date
    ).group_by(Bill.status)
    
    if not current_user.is_admin():
        status_query = status_query.filter(Bill.created_by == current_user.id)
    
    status_data = status_query.all()
    
    # Top customers (by total bill amount)
    customer_query = db.session.query(
        Bill.customer_id,
        func.sum(Bill.total_amount).label('total_amount'),
        func.count(Bill.id).label('bill_count')
    ).filter(
        Bill.created_at >= start_date
    ).group_by(Bill.customer_id).order_by(func.sum(Bill.total_amount).desc()).limit(10)
    
    if not current_user.is_admin():
        customer_query = customer_query.filter(Bill.created_by == current_user.id)
    
    top_customers = customer_query.all()
    
    # Calculate totals
    total_revenue = sum(item.total for item in revenue_data)
    total_expenses = sum(item.total for item in expense_data)
    total_profit = total_revenue - total_expenses

    # Calculate profit growth (compare first and last month)
    profit_growth = 0
    if len(revenue_data) >= 2 and len(expense_data) >= 2:
        # Get first and last month data
        revenue_dict = {item.month: item.total for item in revenue_data}
        expense_dict = {item.month: item.total for item in expense_data}

        months = sorted(set(revenue_dict.keys()) | set(expense_dict.keys()))
        if len(months) >= 2:
            first_month = months[0]
            last_month = months[-1]

            first_profit = revenue_dict.get(first_month, 0) - expense_dict.get(first_month, 0)
            last_profit = revenue_dict.get(last_month, 0) - expense_dict.get(last_month, 0)

            if first_profit != 0:
                profit_growth = ((last_profit - first_profit) / abs(first_profit)) * 100

    # Enhanced analytics data
    analytics_data = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'total_profit': total_profit,
        'profit_growth': profit_growth,
        'revenue_data': revenue_data,
        'expense_data': expense_data,
        'category_data': category_data,
        'status_data': status_data,
        'top_customers': top_customers,
        'period': period,
        'start_date': start_date,
        'end_date': end_date
    }

    return render_template('dashboard/analytics.html', **analytics_data)

@dashboard_bp.route('/api/chart-data')
@login_required
def chart_data():
    chart_type = request.args.get('type', 'revenue')
    period = request.args.get('period', '12months')
    
    # Calculate date range
    end_date = datetime.now()
    if period == '1month':
        start_date = end_date - timedelta(days=30)
    elif period == '3months':
        start_date = end_date - timedelta(days=90)
    elif period == '6months':
        start_date = end_date - timedelta(days=180)
    else:  # 12months
        start_date = end_date - timedelta(days=365)
    
    if chart_type == 'revenue':
        query = db.session.query(
            func.strftime('%Y-%m', Bill.created_at).label('month'),
            func.sum(Bill.total_amount).label('total')
        ).filter(
            Bill.status == 'paid',
            Bill.created_at >= start_date
        ).group_by(func.strftime('%Y-%m', Bill.created_at))
        
        if not current_user.is_admin():
            query = query.filter(Bill.created_by == current_user.id)
        
        data = query.all()
        
        return jsonify({
            'labels': [item.month for item in data],
            'data': [float(item.total) for item in data],
            'label': 'Revenue'
        })
    
    elif chart_type == 'expenses':
        query = db.session.query(
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.date >= start_date
        ).group_by(func.strftime('%Y-%m', Expense.date))
        
        if not current_user.is_admin():
            query = query.filter(Expense.created_by == current_user.id)
        
        data = query.all()
        
        return jsonify({
            'labels': [item.month for item in data],
            'data': [float(item.total) for item in data],
            'label': 'Expenses'
        })
    
    elif chart_type == 'profit':
        # Get revenue data
        revenue_query = db.session.query(
            func.strftime('%Y-%m', Bill.created_at).label('month'),
            func.sum(Bill.total_amount).label('total')
        ).filter(
            Bill.status == 'paid',
            Bill.created_at >= start_date
        ).group_by(func.strftime('%Y-%m', Bill.created_at))
        
        if not current_user.is_admin():
            revenue_query = revenue_query.filter(Bill.created_by == current_user.id)
        
        revenue_data = {item.month: float(item.total) for item in revenue_query.all()}

        # Get expense data
        expense_query = db.session.query(
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.date >= start_date
        ).group_by(func.strftime('%Y-%m', Expense.date))
        
        if not current_user.is_admin():
            expense_query = expense_query.filter(Expense.created_by == current_user.id)
        
        expense_data = {item.month: float(item.total) for item in expense_query.all()}
        
        # Calculate profit for each month
        all_months = set(revenue_data.keys()) | set(expense_data.keys())
        profit_data = []
        labels = []
        
        for month in sorted(all_months):
            revenue = revenue_data.get(month, 0)
            expenses = expense_data.get(month, 0)
            profit = revenue - expenses
            profit_data.append(profit)
            labels.append(month)
        
        return jsonify({
            'labels': labels,
            'data': profit_data,
            'label': 'Profit'
        })
    
    elif chart_type == 'category_expenses':
        query = db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.date >= start_date
        ).group_by(Expense.category)
        
        if not current_user.is_admin():
            query = query.filter(Expense.created_by == current_user.id)
        
        data = query.all()
        
        return jsonify({
            'labels': [item.category for item in data],
            'data': [float(item.total) for item in data],
            'label': 'Expenses by Category'
        })
    
    return jsonify({'error': 'Invalid chart type'})

@dashboard_bp.route('/profit-loss')
@login_required
def profit_loss():
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Revenue calculation
    revenue_query = db.session.query(func.sum(Bill.total_amount)).filter(
        Bill.status == 'paid',
        Bill.created_at >= start_dt,
        Bill.created_at <= end_dt
    )
    
    if not current_user.is_admin():
        revenue_query = revenue_query.filter(Bill.created_by == current_user.id)
    
    total_revenue = revenue_query.scalar() or 0
    
    # Expense calculation
    expense_query = db.session.query(func.sum(Expense.amount)).filter(
        Expense.date >= start_dt,
        Expense.date <= end_dt
    )
    
    if not current_user.is_admin():
        expense_query = expense_query.filter(Expense.created_by == current_user.id)
    
    total_expenses = expense_query.scalar() or 0
    
    # Calculate profit/loss
    net_profit = total_revenue - total_expenses
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return render_template('dashboard/profit_loss.html',
                         total_revenue=total_revenue,
                         total_expenses=total_expenses,
                         net_profit=net_profit,
                         profit_margin=profit_margin,
                         start_date=start_date,
                         end_date=end_date)
