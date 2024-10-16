from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.data import *
from app.models import Product

# create the inventory management blueprint
inventory = Blueprint('inventory', __name__)

# ROUTES

# inventory home endpoint
@inventory.route('/inventory', methods=['GET'])
def inventory_home():

    # get all products from the database
    products = Product.query.all()

    products_dict = parse_product_data(products)

    print(products_dict)

    # dictionary of items to pass to the template
    jinja_vars = {
        'items': [
            {'name': 'item1', 'quantity': 5, 'id': 1},
            {'name': 'item2', 'quantity': 10, 'id': 2},
            {'name': 'item3', 'quantity': 15, 'id': 3},
        ],

        # get all products from the database
        'products': products_dict
    }

    return render_template('inventory.html', **jinja_vars)

# inventory updates endpoint
@inventory.route('/inventory_update', methods=['GET', 'POST'])
def inventory_update():

    products = Product.query.filter(Product.quantity > 0).all()

    # dictionary of items to pass to the template
    jinja_vars = {
        'items': [
            {'name': 'item1', 'quantity': 5, 'id': 1},
            {'name': 'item2', 'quantity': 10, 'id': 2},
            {'name': 'item3', 'quantity': 15, 'id': 3},
        ],

        # get all products from the database
        'products': products
    }

    # 
    if request.method == 'POST':

        print(request.form)

    return render_template('inventory.html', **jinja_vars)

