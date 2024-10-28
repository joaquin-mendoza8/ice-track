from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.data import *
from app.models import Product, User
from config.config import db

# create the order entry form blueprint
order = Blueprint('order', __name__)

# inventory home endpoint
@order.route('/order', methods=['GET'])
def order_home():
    return render_template('order.html')