from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.data import *
from app.models import Product
from config.config import db

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


@inventory.route('/inventory_update', methods=['GET', 'POST'])
def inventory_update_product():
    
        # check if the form was submitted
        if request.method == 'POST':
    
            print(request.form)

            # extract form data
            product_id = request.form['product-id']
            product_flavor = request.form['product-flavor']
            product_price = request.form['product-price']
            product_quantity = request.form['product-quantity']

            # ensure all fields are filled
            if (product_id and product_flavor and product_price and product_quantity):
                 
                # find the product in the database
                product = Product.query.get(product_id)

                # if product exists, update it
                if product:
                    product.flavor = product_flavor
                    product.price = product_price
                    product.quantity = product_quantity

                    # commit the changes
                    db.session.commit()

                    # redirect to the inventory page
                    return redirect(url_for('inventory.inventory_home'))
    
        return redirect(url_for('inventory.inventory_home'))
    
@inventory.route('/orders', methods=['GET'])
def shipping():
        return render_template('orders.html')
    
@inventory.route('/shipments', methods=['GET'])
def shipping():
        return render_template('shipments.html')
    

@inventory.route('/tickets', methods=['GET'])
def shipping():
        return render_template('tickets.html')