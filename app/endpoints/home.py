from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import current_user, login_required

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
