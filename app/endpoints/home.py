from flask import Blueprint, request, render_template, redirect, url_for, send_from_directory
from flask_login import current_user, login_required
import os

# create the home blueprint
home = Blueprint('home', __name__)

# create the home endpoint
@home.route('/')
@login_required
def home_home():

    # if user is not logged in, redirect to login
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return redirect(url_for('inventory.inventory_home')) # TODO: change to home page

# create the favicon endpoint
@home.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(os.path.dirname(home.root_path), 'static/images'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
