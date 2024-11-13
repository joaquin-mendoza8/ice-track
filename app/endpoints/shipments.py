from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required
from app.utils.data import *
from app.models import Product, User, Order, OrderItem
from app.extensions import db

# create the shipments blueprint
shipments = Blueprint('shipments', __name__)

# shipments home endpoint
@shipments.route('/shipments', methods=['GET'])
@login_required
def shipments_home():
    return render_template('shipments/shipments.html')