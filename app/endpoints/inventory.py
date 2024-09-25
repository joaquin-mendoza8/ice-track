from flask import Blueprint, request, redirect, url_for, render_template
from app.models import Product

# create the inventory management blueprint
inventory = Blueprint('inventory', __name__)

# ROUTES

# create the inventory home endpoint
@inventory.route('/inventory_update', methods=['GET', 'POST'])
def inventory_home():

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

