from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.data import *
from app.models import Product, User, Order, OrderItem
from config.config import db

# create the trouble tickets blueprint
tickets = Blueprint('tickets', __name__)

# tickets home endpoint
@tickets.route('/tickets', methods=['GET'])
def tickets_home():
    return render_template('tickets.html')