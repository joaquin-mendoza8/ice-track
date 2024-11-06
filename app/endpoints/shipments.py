from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.data import *
from app.models import Product, User, Order, OrderItem
from config.config import db

# create the shipments blueprint
shipments = Blueprint('shipments', __name__)

# shipments home endpoint
@shipments.route('/shipments', methods=['GET'])
def shipments_home():
    return render_template('shipments.html')