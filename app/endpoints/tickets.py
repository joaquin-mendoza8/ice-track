from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.data import *
# from app.models import Product
# from app.models import Order
# from app.models import Customer
from config.config import db
from datetime import datetime

# create the inventory management blueprint
tickets = Blueprint('tickets', __name__)

@tickets.route('/tickets', methods=['GET'])
def tickets_home():
	return render_template('tickets.html')