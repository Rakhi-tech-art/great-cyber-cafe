from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Expense, ExpenseCategory, db
from datetime import datetime
from sqlalchemy import func
from routes.auth import admin_required

expense_bp = Blueprint('expense', __name__)

@expense_bp.route('/')
@login_required
def expenses():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    query = Expense.query.filter_by(created_by=current_user.id)
    
    if category:
        query = query.filter_by(category=category)
    
    if start_date:
        query = query.filter(Expense.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        query = query.filter(Expense.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    expenses = query.order_by(Expense.date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Get categories for filter
    categories = db.session.query(Expense.category).distinct().all()
    categories = [c[0] for c in categories]
    
    # Calculate total for current filter
    total_amount = query.with_entities(func.sum(Expense.amount)).scalar() or 0
    
    return render_template('expense/expenses.html', 
                         expenses=expenses, 
                         categories=categories,
                         selected_category=category,
                         start_date=start_date,
                         end_date=end_date,
                         total_amount=total_amount)

@expense_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        
        expense = Expense(
            title=title,
            description=description,
            amount=amount,
            category=category,
            date=date,
            created_by=current_user.id
        )
        
        db.session.add(expense)
        db.session.commit()
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expense.expenses'))
    
    # Get existing categories
    categories = db.session.query(Expense.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    # Default categories
    default_categories = [
        'Office Supplies', 'Travel', 'Meals', 'Utilities', 'Software', 
        'Marketing', 'Equipment', 'Rent', 'Insurance', 'Other'
    ]
    
    # Combine and remove duplicates
    all_categories = list(set(categories + default_categories))
    all_categories.sort()
    
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    return render_template('expense/create.html', categories=all_categories, today=today)

@expense_bp.route('/<int:id>')
@login_required
def view(id):
    expense = Expense.query.get_or_404(id)
    
    if expense.created_by != current_user.id:
        flash('You do not have permission to view this expense.', 'error')
        return redirect(url_for('expense.expenses'))
    
    return render_template('expense/view.html', expense=expense)

@expense_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    expense = Expense.query.get_or_404(id)
    
    if expense.created_by != current_user.id:
        flash('You do not have permission to edit this expense.', 'error')
        return redirect(url_for('expense.expenses'))
    
    if request.method == 'POST':
        expense.title = request.form.get('title')
        expense.description = request.form.get('description')
        expense.amount = float(request.form.get('amount'))
        expense.category = request.form.get('category')
        expense.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        
        db.session.commit()
        
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expense.view', id=expense.id))
    
    # Get existing categories
    categories = db.session.query(Expense.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    # Default categories
    default_categories = [
        'Office Supplies', 'Travel', 'Meals', 'Utilities', 'Software', 
        'Marketing', 'Equipment', 'Rent', 'Insurance', 'Other'
    ]
    
    # Combine and remove duplicates
    all_categories = list(set(categories + default_categories))
    all_categories.sort()
    
    return render_template('expense/edit.html', expense=expense, categories=all_categories)

@expense_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    expense = Expense.query.get_or_404(id)
    
    if expense.created_by != current_user.id:
        flash('You do not have permission to delete this expense.', 'error')
        return redirect(url_for('expense.expenses'))
    
    db.session.delete(expense)
    db.session.commit()
    
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expense.expenses'))

@expense_bp.route('/reports')
@login_required
def reports():
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category', '')
    
    query = Expense.query.filter_by(created_by=current_user.id)
    
    if start_date:
        query = query.filter(Expense.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        query = query.filter(Expense.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    if category:
        query = query.filter_by(category=category)
    
    expenses = query.all()
    
    # Calculate statistics
    total_amount = sum(expense.amount for expense in expenses)
    
    # Group by category
    category_stats = {}
    for expense in expenses:
        if expense.category not in category_stats:
            category_stats[expense.category] = {
                'amount': 0,
                'count': 0
            }
        category_stats[expense.category]['amount'] += expense.amount
        category_stats[expense.category]['count'] += 1
    
    # Group by month
    monthly_stats = {}
    for expense in expenses:
        month_key = expense.date.strftime('%Y-%m')
        if month_key not in monthly_stats:
            monthly_stats[month_key] = 0
        monthly_stats[month_key] += expense.amount
    
    # Get categories for filter
    categories = db.session.query(Expense.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('expense/reports.html',
                         expenses=expenses,
                         total_amount=total_amount,
                         category_stats=category_stats,
                         monthly_stats=monthly_stats,
                         categories=categories,
                         start_date=start_date,
                         end_date=end_date,
                         selected_category=category)

@expense_bp.route('/categories')
@login_required
@admin_required
def categories():
    categories = ExpenseCategory.query.all()
    return render_template('expense/categories.html', categories=categories)
