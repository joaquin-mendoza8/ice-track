from flask import Blueprint, render_template
from app.utils.admin_decorator import admin_required

# create the admin blueprint
admin = Blueprint('admin', __name__)


# ROUTES

# admin dashboard endpoint
@admin.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

# TODO: add admin functionalities (e.g. user management, 
#                                       order limits, 
#                                       user-defined lists, 
#                                       etc.)