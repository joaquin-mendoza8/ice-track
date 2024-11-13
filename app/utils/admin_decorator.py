from flask import url_for, flash, request, redirect
from flask_login import current_user


def admin_required(f):
    """Decorator to restrict access to admin users."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', category='warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', category='danger')
            return redirect(request.referrer or url_for('inventory.inventory_home'))
        return f(*args, **kwargs)
    return decorated_function