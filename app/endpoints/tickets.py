from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required
from app.utils.data import *
from app.models import Product, User, Order, OrderItem
from app.extensions import db

# create the trouble tickets blueprint
tickets = Blueprint('tickets', __name__)

# tickets home endpoint
@tickets.route('/tickets', methods=['GET'])
@login_required
def tickets_home():
    return render_template('tickets/tickets.html')