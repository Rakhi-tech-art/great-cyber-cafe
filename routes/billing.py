from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from models import Bill, BillItem, Customer, db
from datetime import datetime, timedelta
import os
from utils.pdf_generator import generate_bill_pdf
from utils.email_sender import send_bill_email
from sqlalchemy import and_
from routes.auth import admin_required

# Try to import WhatsApp functionality, but make it optional
try:
    from utils.whatsapp_sender import send_whatsapp_message
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    send_whatsapp_message = None

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/bills')
@login_required
def bills():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = Bill.query.filter_by(created_by=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.join(Customer).filter(
            Customer.name.contains(search) | 
            Bill.bill_number.contains(search)
        )
    
    bills = query.order_by(Bill.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    from datetime import datetime
    today = datetime.now().date()
    return render_template('billing/bills.html', bills=bills, status=status, search=search, today=today)

@billing_bp.route('/bills/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        # Get customer data
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_contact = request.form.get('customer_contact')

        # Check if customer exists
        customer = Customer.query.filter_by(email=customer_email).first()
        if not customer:
            customer = Customer(
                name=customer_name,
                email=customer_email,
                phone=customer_contact,  # Store contact in phone field
                whatsapp=customer_contact,  # Also store in whatsapp field for compatibility
                address=''  # Empty address
            )
            db.session.add(customer)
            db.session.flush()
        
        # Generate bill number
        last_bill = Bill.query.order_by(Bill.id.desc()).first()
        bill_number = f"INV-{(last_bill.id + 1) if last_bill else 1:06d}"
        
        # Get advance amount
        advance_amount = float(request.form.get('advance_amount', 0))

        # Create bill with simplified data
        bill = Bill(
            bill_number=bill_number,
            customer_id=customer.id,
            created_by=current_user.id,
            tax_rate=0.0,  # No tax
            discount=0.0,  # No discount
            notes='',      # No notes
            due_date=None, # No due date
            advance_amount=advance_amount
        )
        
        db.session.add(bill)
        db.session.flush()
        
        # Add bill items
        items_data = []
        for key in request.form.keys():
            if key.startswith('items[') and key.endswith('][description]'):
                index = key.split('[')[1].split(']')[0]
                description = request.form.get(f'items[{index}][description]')

                # Safe float conversion with error handling
                try:
                    quantity_str = request.form.get(f'items[{index}][quantity]', '1')
                    rate_str = request.form.get(f'items[{index}][rate]', '0')

                    quantity = float(quantity_str) if quantity_str.strip() else 1.0
                    rate = float(rate_str) if rate_str.strip() else 0.0
                except (ValueError, AttributeError):
                    quantity = 1.0
                    rate = 0.0

                if description and description.strip() and rate > 0:
                    total = quantity * rate
                    bill_item = BillItem(
                        bill_id=bill.id,
                        description=description.strip(),
                        quantity=quantity,
                        rate=rate,
                        total=total
                    )
                    db.session.add(bill_item)
        
        # Calculate totals
        bill.calculate_totals()
        db.session.commit()
        
        flash('Bill created successfully!', 'success')
        return redirect(url_for('billing.view', id=bill.id))
    
    from datetime import date, datetime
    today = date.today().strftime('%Y-%m-%d')
    current_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')
    customers = Customer.query.all()
    return render_template('billing/create.html', customers=customers, today=today, current_datetime=current_datetime)

@billing_bp.route('/bills/<int:id>')
@login_required
def view(id):
    bill = Bill.query.get_or_404(id)
    
    if bill.created_by != current_user.id:
        flash('You do not have permission to view this bill.', 'error')
        return redirect(url_for('billing.bills'))
    
    return render_template('billing/view.html', bill=bill)

@billing_bp.route('/bills/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    bill = Bill.query.get_or_404(id)
    
    if bill.created_by != current_user.id:
        flash('You do not have permission to edit this bill.', 'error')
        return redirect(url_for('billing.bills'))
    
    if request.method == 'POST':
        # Update customer data with simplified fields
        bill.customer.name = request.form.get('customer_name')
        bill.customer.email = request.form.get('customer_email')
        customer_contact = request.form.get('customer_contact')
        bill.customer.phone = customer_contact
        bill.customer.whatsapp = customer_contact
        bill.customer.address = ''

        # Update bill data with simplified values
        bill.tax_rate = 0.0
        bill.discount = 0.0
        bill.notes = ''
        bill.due_date = None
        
        # Clear existing items
        BillItem.query.filter_by(bill_id=bill.id).delete()
        
        # Add updated items with error handling
        for key in request.form.keys():
            if key.startswith('items[') and key.endswith('][description]'):
                index = key.split('[')[1].split(']')[0]
                description = request.form.get(f'items[{index}][description]')

                # Safe float conversion with error handling
                try:
                    quantity_str = request.form.get(f'items[{index}][quantity]', '1')
                    rate_str = request.form.get(f'items[{index}][rate]', '0')

                    quantity = float(quantity_str) if quantity_str.strip() else 1.0
                    rate = float(rate_str) if rate_str.strip() else 0.0
                except (ValueError, AttributeError):
                    quantity = 1.0
                    rate = 0.0

                if description and description.strip() and rate > 0:
                    total = quantity * rate
                    bill_item = BillItem(
                        bill_id=bill.id,
                        description=description.strip(),
                        quantity=quantity,
                        rate=rate,
                        total=total
                    )
                    db.session.add(bill_item)
        
        # Calculate totals
        bill.calculate_totals()
        db.session.commit()
        
        flash('Bill updated successfully!', 'success')
        return redirect(url_for('billing.view', id=bill.id))
    
    return render_template('billing/edit.html', bill=bill)

@billing_bp.route('/bills/<int:id>/pdf')
@login_required
def download_pdf(id):
    bill = Bill.query.get_or_404(id)
    
    if bill.created_by != current_user.id:
        flash('You do not have permission to access this bill.', 'error')
        return redirect(url_for('billing.bills'))
    
    pdf_path = generate_bill_pdf(bill)
    return send_file(pdf_path, as_attachment=True, download_name=f'{bill.bill_number}.pdf')

@billing_bp.route('/bills/<int:id>/send', methods=['POST'])
@login_required
def send_bill(id):
    bill = Bill.query.get_or_404(id)
    
    if bill.created_by != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    send_email = request.json.get('send_email', False)
    send_whatsapp = request.json.get('send_whatsapp', False)
    
    success = True
    messages = []
    
    if send_email and bill.customer.email:
        try:
            pdf_path = generate_bill_pdf(bill)
            send_bill_email(bill, pdf_path)
            bill.email_sent = True
            messages.append('Email sent successfully')
        except Exception as e:
            success = False
            messages.append(f'Email failed: {str(e)}')
    
    if send_whatsapp and bill.customer.whatsapp:
        if not WHATSAPP_AVAILABLE:
            success = False
            messages.append('WhatsApp functionality is not available in this environment')
        else:
            try:
                pdf_path = generate_bill_pdf(bill)
                send_whatsapp_message(bill, pdf_path)
                bill.whatsapp_sent = True
                messages.append('WhatsApp message sent successfully')
            except Exception as e:
                success = False
                messages.append(f'WhatsApp failed: {str(e)}')
    
    if success:
        bill.status = 'sent'
    
    db.session.commit()
    
    return jsonify({
        'success': success,
        'message': '; '.join(messages)
    })

@billing_bp.route('/bills/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    bill = Bill.query.get_or_404(id)

    if bill.created_by != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'})

    new_status = request.json.get('status')
    if new_status in ['draft', 'sent', 'paid', 'cancelled']:
        bill.status = new_status
        if new_status == 'paid':
            bill.paid_date = datetime.utcnow()
            # When marking as paid, set advance_amount to total_amount
            bill.advance_amount = bill.total_amount
            bill.remaining_amount = 0.0
        db.session.commit()
        return jsonify({'success': True, 'message': f'Status updated to {new_status}'})

    return jsonify({'success': False, 'message': 'Invalid status'})

@billing_bp.route('/bills/<int:id>/payment', methods=['POST'])
@login_required
def update_payment(id):
    bill = Bill.query.get_or_404(id)

    if bill.created_by != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'})

    try:
        payment_amount = float(request.json.get('payment_amount', 0))

        if payment_amount < 0:
            return jsonify({'success': False, 'message': 'Payment amount cannot be negative'})

        if payment_amount > bill.remaining_amount:
            return jsonify({'success': False, 'message': 'Payment amount cannot exceed remaining amount'})

        # Update advance amount and recalculate remaining
        bill.advance_amount += payment_amount
        bill.remaining_amount = max(0, bill.total_amount - bill.advance_amount)

        # Update status based on payment
        if bill.remaining_amount == 0:
            bill.status = 'paid'
            bill.paid_date = datetime.utcnow()
        elif bill.advance_amount > 0:
            bill.status = 'sent'  # Partial payment

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Payment of Rs {payment_amount:.2f} recorded successfully',
            'new_advance_amount': bill.advance_amount,
            'new_remaining_amount': bill.remaining_amount,
            'new_status': bill.status
        })

    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid payment amount'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating payment: {str(e)}'})

@billing_bp.route('/bills/<int:id>/duplicate', methods=['POST'])
@login_required
def duplicate_bill(id):
    original_bill = Bill.query.get_or_404(id)

    if original_bill.created_by != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'})

    try:
        # Generate new bill number
        last_bill = Bill.query.order_by(Bill.id.desc()).first()
        bill_number = f"INV-{(last_bill.id + 1) if last_bill else 1:06d}"

        # Create duplicate bill
        new_bill = Bill(
            bill_number=bill_number,
            customer_id=original_bill.customer_id,
            created_by=current_user.id,
            subtotal=original_bill.subtotal,
            tax_rate=original_bill.tax_rate,
            tax_amount=original_bill.tax_amount,
            discount=original_bill.discount,
            total_amount=original_bill.total_amount,
            advance_amount=0.0,  # Reset advance amount
            remaining_amount=original_bill.total_amount,  # Full amount remaining
            status='draft',  # Reset to draft
            notes=original_bill.notes,
            due_date=original_bill.due_date
        )

        db.session.add(new_bill)
        db.session.flush()

        # Duplicate bill items
        for item in original_bill.items:
            new_item = BillItem(
                bill_id=new_bill.id,
                description=item.description,
                quantity=item.quantity,
                rate=item.rate,
                total=item.total
            )
            db.session.add(new_item)

        db.session.commit()

        return jsonify({'success': True, 'new_bill_id': new_bill.id, 'message': 'Bill duplicated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error duplicating bill: {str(e)}'})

@billing_bp.route('/bills/<int:id>', methods=['DELETE'])
@login_required
def delete_bill(id):
    bill = Bill.query.get_or_404(id)

    if bill.created_by != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'})

    if bill.status == 'paid':
        return jsonify({'success': False, 'message': 'Cannot delete paid invoices'})

    try:
        # Delete bill items first (cascade should handle this, but being explicit)
        BillItem.query.filter_by(bill_id=bill.id).delete()

        # Delete the bill
        db.session.delete(bill)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Bill deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting bill: {str(e)}'})

@billing_bp.route('/today')
@login_required
@admin_required
def today_invoices():
    today = datetime.now().date()
    query = Bill.query.filter(
        db.func.date(Bill.created_at) == today.strftime('%Y-%m-%d'),
        Bill.created_by == current_user.id
    )

    bills = query.order_by(Bill.created_at.desc()).all()

    return render_template('billing/today_invoices.html', bills=bills, date=today)

@billing_bp.route('/last-week')
@login_required
@admin_required
def last_week_invoices():
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)

    query = Bill.query.filter(
        and_(
            Bill.created_at >= week_ago,
            Bill.created_at <= today,
            Bill.created_by == current_user.id
        )
    )

    bills = query.order_by(Bill.created_at.desc()).all()

    return render_template('billing/last_week_invoices.html', bills=bills,
                         start_date=week_ago, end_date=today)

@billing_bp.route('/all')
@login_required
@admin_required
def all_invoices():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = Bill.query.filter_by(created_by=current_user.id)

    if status:
        query = query.filter_by(status=status)

    if search:
        query = query.join(Customer).filter(
            Customer.name.contains(search) |
            Bill.bill_number.contains(search)
        )

    if date_from:
        query = query.filter(Bill.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))

    if date_to:
        query = query.filter(Bill.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))

    bills = query.order_by(Bill.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    from datetime import datetime
    today = datetime.now().date()
    return render_template('billing/all_invoices.html', bills=bills,
                         status=status, search=search, date_from=date_from, date_to=date_to, today=today)

@billing_bp.route('/customers')
@login_required
def customers():
    customers = Customer.query.all()
    return render_template('billing/customers.html', customers=customers)
