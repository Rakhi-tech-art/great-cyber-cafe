from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_from_directory
from flask_login import login_required, current_user
from models import db
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from PIL import Image
from routes.auth import admin_required

settings_bp = Blueprint('settings', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads/profiles'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folder():
    """Create upload folder if it doesn't exist"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@settings_bp.route('/settings')
@login_required
@admin_required
def settings():
    return render_template('settings/settings.html')

@settings_bp.route('/uploads/profiles/<filename>')
def uploaded_file(filename):
    """Serve uploaded profile photos"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@settings_bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile_settings():
    if request.method == 'POST':
        # Update basic profile information
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        
        # Handle profile photo upload
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '' and allowed_file(file.filename):
                create_upload_folder()

                # Delete old profile photo if exists
                if current_user.profile_photo:
                    old_photo_path = current_user.profile_photo
                    if os.path.exists(old_photo_path):
                        try:
                            os.remove(old_photo_path)
                        except Exception as e:
                            flash(f'Warning: Could not delete old photo: {str(e)}', 'warning')

                # Save new photo
                filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                # Resize image
                try:
                    with Image.open(file_path) as img:
                        # Convert to RGB if necessary (for JPEG compatibility)
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                        img.save(file_path, 'JPEG', quality=85)
                except Exception as e:
                    # Clean up the uploaded file if processing fails
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    flash(f'Error processing image: {str(e)}', 'error')
                    return redirect(url_for('settings.profile_settings'))

                # Store relative path for web access
                current_user.profile_photo = file_path
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('settings.profile_settings'))
    
    return render_template('settings/profile.html')

@settings_bp.route('/settings/profile/delete-photo', methods=['POST'])
@login_required
def delete_profile_photo():
    """Delete user's profile photo"""
    try:
        if current_user.profile_photo:
            # Delete the file from filesystem
            photo_path = current_user.profile_photo
            if os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                except Exception as e:
                    return jsonify({'success': False, 'message': f'Error deleting photo file: {str(e)}'})

            # Remove from database
            current_user.profile_photo = None
            db.session.commit()

            # Return JSON response for AJAX request
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': True, 'message': 'Profile photo deleted successfully!'})
            else:
                flash('Profile photo deleted successfully!', 'success')
                return redirect(url_for('settings.profile_settings'))
        else:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': 'No profile photo to delete.'})
            else:
                flash('No profile photo to delete.', 'info')
                return redirect(url_for('settings.profile_settings'))
    except Exception as e:
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        else:
            flash(f'Error deleting photo: {str(e)}', 'error')
            return redirect(url_for('settings.profile_settings'))

@settings_bp.route('/settings/password', methods=['GET', 'POST'])
@login_required
def password_settings():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('settings/password.html')
        
        # Validate new password
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'error')
            return render_template('settings/password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('settings/password.html')
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password updated successfully!', 'success')
        return redirect(url_for('settings.password_settings'))
    
    return render_template('settings/password.html')

@settings_bp.route('/settings/appearance', methods=['GET', 'POST'])
@login_required
def appearance_settings():
    if request.method == 'POST':
        theme = request.form.get('theme')
        if theme in ['light', 'dark']:
            current_user.theme = theme
            db.session.commit()
            flash('Theme updated successfully!', 'success')
        else:
            flash('Invalid theme selection.', 'error')
        
        return redirect(url_for('settings.appearance_settings'))
    
    return render_template('settings/appearance.html')

@settings_bp.route('/api/settings/theme', methods=['POST'])
@login_required
def update_theme():
    """API endpoint to update theme via AJAX"""
    data = request.get_json()
    theme = data.get('theme')
    
    if theme in ['light', 'dark']:
        current_user.theme = theme
        db.session.commit()
        return jsonify({'success': True, 'message': 'Theme updated successfully'})
    
    return jsonify({'success': False, 'message': 'Invalid theme'})

@settings_bp.route('/settings/notifications', methods=['GET', 'POST'])
@login_required
def notification_settings():
    from models import NotificationPreferences
    from datetime import datetime

    # Get or create notification preferences
    prefs = current_user.get_notification_preferences()

    if request.method == 'POST':
        try:
            # Update email notification preferences
            prefs.email_bill_created = 'email_bill_created' in request.form
            prefs.email_bill_paid = 'email_bill_paid' in request.form
            prefs.email_expense_added = 'email_expense_added' in request.form
            prefs.email_weekly_report = 'email_weekly_report' in request.form
            prefs.email_monthly_report = 'email_monthly_report' in request.form
            prefs.email_system_updates = 'email_system_updates' in request.form

            # Update WhatsApp notification preferences
            prefs.whatsapp_bill_paid = 'whatsapp_bill_paid' in request.form
            prefs.whatsapp_daily_summary = 'whatsapp_daily_summary' in request.form
            prefs.whatsapp_overdue = 'whatsapp_overdue' in request.form
            prefs.whatsapp_goals = 'whatsapp_goals' in request.form

            # Update notification schedule
            quiet_start = request.form.get('quiet_hours_start')
            if quiet_start:
                prefs.quiet_hours_start = datetime.strptime(quiet_start, '%H:%M').time()

            quiet_end = request.form.get('quiet_hours_end')
            if quiet_end:
                prefs.quiet_hours_end = datetime.strptime(quiet_end, '%H:%M').time()

            prefs.weekly_report_day = request.form.get('weekly_report_day', 'monday')

            report_time = request.form.get('report_time')
            if report_time:
                prefs.report_time = datetime.strptime(report_time, '%H:%M').time()

            # Update timestamp
            prefs.updated_at = datetime.utcnow()

            db.session.commit()
            flash('Notification settings updated successfully!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating notification settings: {str(e)}', 'error')

        return redirect(url_for('settings.notification_settings'))

    return render_template('settings/notifications.html', prefs=prefs)

@settings_bp.route('/api/settings/test-notification', methods=['POST'])
@login_required
def test_notification():
    """Send a test notification to the user"""
    try:
        from utils.email_sender import send_email

        subject = "Test Notification - Smart Billing System"
        body = f"""
        Dear {current_user.username},

        This is a test notification from your Smart Billing System.

        If you received this email, your notification settings are working correctly!

        Test Details:
        - Sent at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        - User: {current_user.username}
        - Email: {current_user.email}

        Best regards,
        Smart Billing System
        """

        send_email(current_user.email, subject, body)
        return jsonify({
            'success': True,
            'message': f'Test notification sent successfully to {current_user.email}!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to send test notification: {str(e)}'
        })

@settings_bp.route('/settings/account', methods=['GET', 'POST'])
@login_required
@admin_required
def account_settings():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'deactivate':
            # Handle account deactivation
            current_user.is_active = False
            db.session.commit()
            flash('Account deactivated successfully.', 'info')
            return redirect(url_for('auth.logout'))
        
    return render_template('settings/account.html')
