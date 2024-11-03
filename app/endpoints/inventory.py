from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.data import *
from app.models import Product
#from app.models import Order
#from app.models import Customer
from config.config import db
from datetime import datetime

# create the inventory management blueprint
inventory = Blueprint('inventory', __name__)

# ROUTES

# inventory home endpoint
@inventory.route('/inventory', methods=['GET'])
def inventory_home():

    # check if filter key was passed
    filter_key = request.args.get('filter')

    # get all products from the database
    products = Product.query.all()

    # if filter key is passed, sort by that key
    if filter_key:
        products = sorted(products, key=lambda x: getattr(x, filter_key))

    # parse the product data into a dictionary
    products_dict = parse_product_data(products)

    # dictionary of items to pass to the template
    jinja_vars = {
        'products': products_dict
    }

    return render_template('inventory.html', **jinja_vars)

@inventory.route('/inventory_update', methods=['GET', 'POST'])
def inventory_update_product():
    
    # check if the form was submitted
    if request.method == 'POST':
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

@inventory.route('/inventory_add', methods=['GET', 'POST'])
def inventory_add_product():
    if request.method == 'POST':

        # extract the product data from the form
        product_flavor = request.form.get('product-flavor')
        product_price = request.form.get('product-price')
        product_quantity = request.form.get('product-quantity')
        product_status = request.form.get('product-status')

        # ensure all fields are filled
        if (product_flavor and product_price and product_quantity and product_status):

            # convert the price and quantity to float and int
            product_price = float(product_price)
            product_quantity = int(product_quantity)

            # create a new product object
            new_product = Product(flavor=product_flavor, price=product_price, quantity=product_quantity, status=product_status)

            # add the new product to the database
            db.session.add(new_product)
            db.session.commit()

            # log the addition
            print(f'Added product: {new_product}')
            
    return redirect(url_for('inventory.inventory_home'))

@inventory.route('/inventory_delete', methods=['GET', 'POST'])
def inventory_delete_product():
    if request.method == 'POST':
        
        # extract the product id from the form
        product_id = request.form['product-id-delete']

        # find the product in the database
        product = Product.query.get(product_id)

        # if product exists, delete it
        if product:
            db.session.delete(product)
            db.session.commit()

            # TODO: log the deletion
            print(f'Deleted product: {product}')
        else:

            # TODO: log the error / handle the error
            print(f"Product not found: {product}")

    # redirect to the inventory page
    return redirect(url_for('inventory.inventory_home'))