from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import WorkEntry, db
from datetime import datetime
from sqlalchemy import func

work_bp = Blueprint('work', __name__)

@work_bp.route('/entries')
@login_required
def entries():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    project = request.args.get('project', '')
    
    query = WorkEntry.query.filter_by(user_id=current_user.id)
    
    if status:
        query = query.filter_by(work_status=status)
    
    if project:
        query = query.filter(WorkEntry.project_name.contains(project))
    
    entries = query.order_by(WorkEntry.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    # Get unique projects for filter
    projects_query = WorkEntry.query.with_entities(WorkEntry.project_name).distinct().filter_by(user_id=current_user.id)
    projects = [p[0] for p in projects_query.all()]

    return render_template('work/entries.html', entries=entries, status=status,
                         project=project, projects=projects)

@work_bp.route('/entries/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        # Customer Information
        customer_name = request.form.get('customer_name')
        customer_phone = request.form.get('customer_phone')

        # Service Information
        service_type = request.form.get('service_type')
        project_name = request.form.get('project_name')

        # Billing Information
        hourly_rate = float(request.form.get('hourly_rate', 0))
        advance_amount = float(request.form.get('advance_amount', 0))
        work_status = request.form.get('work_status', 'in_progress')

        work_entry = WorkEntry(
            user_id=current_user.id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            service_type=service_type,
            project_name=project_name,
            task_description=f"{service_type.replace('_', ' ').title()} service for {customer_name}",
            start_time=datetime.utcnow(),
            hourly_rate=hourly_rate,
            advance_amount=advance_amount,
            work_status=work_status
        )

        # Set initial total amount to hourly rate (1 hour minimum)
        work_entry.total_amount = hourly_rate
        work_entry.remaining_amount = max(0, hourly_rate - advance_amount)

        # Set payment status based on advance amount
        if advance_amount >= hourly_rate:
            work_entry.payment_status = 'paid'
        elif advance_amount > 0:
            work_entry.payment_status = 'partial'
        else:
            work_entry.payment_status = 'pending'

        db.session.add(work_entry)
        db.session.commit()

        flash('Work entry created successfully!', 'success')
        return redirect(url_for('work.entries'))

    return render_template('work/create.html')

@work_bp.route('/entries/<int:id>')
@login_required
def view(id):
    work_entry = WorkEntry.query.get_or_404(id)
    
    if work_entry.user_id != current_user.id:
        flash('You do not have permission to view this work entry.', 'error')
        return redirect(url_for('work.entries'))
    
    return render_template('work/view.html', work_entry=work_entry)

@work_bp.route('/entries/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    work_entry = WorkEntry.query.get_or_404(id)
    
    if work_entry.user_id != current_user.id:
        flash('You do not have permission to edit this work entry.', 'error')
        return redirect(url_for('work.entries'))
    
    if request.method == 'POST':
        # Update customer information
        work_entry.customer_name = request.form.get('customer_name')
        work_entry.customer_phone = request.form.get('customer_phone')
        work_entry.service_type = request.form.get('service_type')

        # Update work information
        work_entry.project_name = request.form.get('project_name')
        work_entry.task_description = request.form.get('task_description')
        work_entry.hourly_rate = float(request.form.get('hourly_rate', 0))
        work_entry.advance_amount = float(request.form.get('advance_amount', 0))
        work_entry.work_status = request.form.get('work_status', 'in_progress')
        work_entry.payment_status = request.form.get('payment_status', 'pending')

        # Set total amount to hourly rate (fixed amount)
        work_entry.total_amount = work_entry.hourly_rate
        work_entry.remaining_amount = max(0, work_entry.total_amount - work_entry.advance_amount)

        # Update payment status based on advance amount
        if work_entry.advance_amount >= work_entry.total_amount:
            work_entry.payment_status = 'paid'
        elif work_entry.advance_amount > 0:
            work_entry.payment_status = 'partial'
        else:
            work_entry.payment_status = 'pending'
        
        db.session.commit()
        
        flash('Work entry updated successfully!', 'success')
        return redirect(url_for('work.view', id=work_entry.id))
    
    return render_template('work/edit.html', work_entry=work_entry)

@work_bp.route('/entries/<int:id>/stop', methods=['POST'])
@login_required
def stop_timer(id):
    work_entry = WorkEntry.query.get_or_404(id)
    
    if work_entry.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    if work_entry.work_status != 'in_progress':
        return jsonify({'success': False, 'message': 'Timer is not running'})

    work_entry.end_time = datetime.utcnow()
    work_entry.work_status = 'completed'
    work_entry.calculate_duration()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Timer stopped successfully',
        'duration': work_entry.duration_minutes,
        'total_amount': work_entry.total_amount
    })

@work_bp.route('/entries/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    work_entry = WorkEntry.query.get_or_404(id)
    
    if work_entry.user_id != current_user.id:
        flash('You do not have permission to delete this work entry.', 'error')
        return redirect(url_for('work.entries'))
    
    db.session.delete(work_entry)
    db.session.commit()
    
    flash('Work entry deleted successfully!', 'success')
    return redirect(url_for('work.entries'))

@work_bp.route('/entries/<int:id>/payment-info')
@login_required
def payment_info(id):
    work_entry = WorkEntry.query.get_or_404(id)

    if work_entry.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'})

    return jsonify({
        'success': True,
        'total_amount': work_entry.total_amount or 0,
        'paid_amount': work_entry.advance_amount or 0,
        'remaining_amount': work_entry.remaining_amount or 0,
        'payment_status': work_entry.payment_status or 'pending'
    })

@work_bp.route('/entries/<int:id>/update-payment', methods=['POST'])
@login_required
def update_payment(id):
    work_entry = WorkEntry.query.get_or_404(id)

    if work_entry.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'})

    try:
        data = request.get_json()
        payment_amount = float(data.get('payment_amount', 0))

        if payment_amount < 0:
            return jsonify({'success': False, 'message': 'Payment amount cannot be negative'})

        # Update advance amount (paid amount)
        current_paid = work_entry.advance_amount or 0
        new_paid_amount = current_paid + payment_amount

        # Ensure we don't overpay
        total_amount = work_entry.total_amount or 0
        if new_paid_amount > total_amount:
            return jsonify({'success': False, 'message': 'Payment amount exceeds total amount'})

        work_entry.advance_amount = new_paid_amount

        # Update payment status
        if new_paid_amount >= total_amount:
            work_entry.payment_status = 'paid'
        elif new_paid_amount > 0:
            work_entry.payment_status = 'partial'
        else:
            work_entry.payment_status = 'pending'

        # Calculate remaining amount
        work_entry.remaining_amount = total_amount - new_paid_amount

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Payment updated successfully',
            'new_paid_amount': new_paid_amount,
            'remaining_amount': work_entry.remaining_amount,
            'payment_status': work_entry.payment_status
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@work_bp.route('/entries/<int:id>/work-status-info')
@login_required
def work_status_info(id):
    work_entry = WorkEntry.query.get_or_404(id)

    if work_entry.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'})

    return jsonify({
        'success': True,
        'work_status': work_entry.work_status or 'pending'
    })

@work_bp.route('/entries/<int:id>/update-work-status', methods=['POST'])
@login_required
def update_work_status(id):
    work_entry = WorkEntry.query.get_or_404(id)

    if work_entry.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'})

    try:
        data = request.get_json()
        new_status = data.get('work_status')

        valid_statuses = ['pending', 'in_progress', 'completed', 'delivered']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'Invalid work status'})

        work_entry.work_status = new_status

        # If marking as completed or delivered, set end time if not already set
        if new_status in ['completed', 'delivered'] and not work_entry.end_time:
            work_entry.end_time = datetime.utcnow()
            work_entry.calculate_duration()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Work status updated to {new_status.replace("_", " ").title()}',
            'new_work_status': new_status
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@work_bp.route('/reports')
@login_required
def reports():
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    project = request.args.get('project', '')
    
    query = WorkEntry.query.filter_by(work_status='completed', user_id=current_user.id)
    
    if start_date:
        query = query.filter(WorkEntry.start_time >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        query = query.filter(WorkEntry.start_time <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    if project:
        query = query.filter(WorkEntry.project_name.contains(project))
    
    entries = query.all()
    
    # Calculate statistics
    total_hours = sum(entry.duration_minutes or 0 for entry in entries) / 60
    total_amount = sum(entry.total_amount or 0 for entry in entries)
    
    # Group by project
    project_stats = {}
    for entry in entries:
        if entry.project_name not in project_stats:
            project_stats[entry.project_name] = {
                'hours': 0,
                'amount': 0,
                'entries': 0
            }
        project_stats[entry.project_name]['hours'] += (entry.duration_minutes or 0) / 60
        project_stats[entry.project_name]['amount'] += entry.total_amount or 0
        project_stats[entry.project_name]['entries'] += 1
    
    # Get unique projects for filter
    projects_query = WorkEntry.query.with_entities(WorkEntry.project_name).distinct().filter_by(user_id=current_user.id)
    projects = [p[0] for p in projects_query.all()]
    
    return render_template('work/reports.html', 
                         entries=entries,
                         total_hours=total_hours,
                         total_amount=total_amount,
                         project_stats=project_stats,
                         projects=projects,
                         start_date=start_date,
                         end_date=end_date,
                         selected_project=project)

@work_bp.route('/timer')
@login_required
def timer():
    # Get active timer for current user
    active_timer = WorkEntry.query.filter_by(
        user_id=current_user.id,
        work_status='in_progress'
    ).first()
    
    return render_template('work/timer.html', active_timer=active_timer)
