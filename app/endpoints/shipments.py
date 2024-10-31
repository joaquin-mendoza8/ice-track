from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.data import *
from config.config import db
from datetime import datetime
# from app.models import Product
# from app.models import Order
# from app.models import Customer

# create the inventory management blueprint
shipments = Blueprint('shipments', __name__)

@shipments.route('/shipments', methods=['GET'])
def shipments_home():
    return render_template('shipments.html')