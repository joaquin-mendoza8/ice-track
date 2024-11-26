from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required
from app.utils.data import *
from app.utils.fetch_settings import fetch_autosignoff_interval, \
    fetch_supported_container_sizes, fetch_supported_flavors
from app.models import Product, User , Log
from app.extensions import db
from datetime import datetime

# create the inventory management blueprint
inventory = Blueprint('inventory', __name__)

# template paths

# ROUTES

# inventory home endpoint
@inventory.route('/inventory', methods=['GET'])
@login_required
def inventory_home():

    # check if filter key was passed
    filter_key = request.args.get('filter')

    # get all products from the database
    products = Product.query.filter_by(deleted_at=None).all()

    # if filter key is passed, sort by that key
    if filter_key:
        products = sorted(products, key=lambda x: getattr(x, filter_key))

    # fetch the supported container sizes from the database
    container_sizes = fetch_supported_container_sizes()

    # fetch the supported flavors from the database
    supported_flavors = fetch_supported_flavors()

    # parse the product data into a dictionary
    products_dict = parse_product_data(products)
    
    # fetch all logs from the database
    logs = Log.query.order_by(Log.timestamp.desc()).all()

    # dictionary of items to pass to the template
    jinja_vars = {
        'products': products_dict,
        'logs' : logs, # pass logs to the template,
        'supported_container_sizes': container_sizes,
        'supported_flavors': supported_flavors
    }

    return render_template('inventory/inventory.html', **jinja_vars)


# inventory update endpoint
@inventory.route('/inventory_update', methods=['GET', 'POST'])
@login_required
def inventory_update_product():
    
    # check if the form was submitted
    if request.method == 'POST':

        # extract form data
        product_id = request.form.get('product-id')
        product_flavor = request.form.get('product-flavor')
        product_container_size = request.form.get('product-container-size')
        product_price = request.form.get('product-price')
        product_quantity = request.form.get('product-quantity')
        product_status = request.form.get('product-status')

        # ensure all fields are filled
        if all([product_id, product_flavor, product_container_size,
                product_price, product_quantity, product_status]):
                
            # find the product in the database
            product = Product.query.get(product_id)

            # if product exists, update it
            if product:
                product.flavor = product_flavor
                product.container_size = product_container_size
                product.price = product_price
                product.quantity = product_quantity
                product.status = product_status

                # commit the changes
                db.session.commit()

            else:

                # TODO: log the error / handle the error
                print(f"Product not found: {product}")

        else:

            # TODO: log the error / handle the error
            print(f"Missing fields: {product_id, product_flavor, product_container_size, product_price, product_quantity, product_status}")

    # redirect to the inventory page
    return redirect(url_for('inventory.inventory_home'))


# inventory add endpoint
@inventory.route('/inventory_add', methods=['GET', 'POST'])
@login_required
def inventory_add_product():
    if request.method == 'POST':

        # extract the product data from the form
        product_flavor = request.form.get('product-flavor-add')
        product_container_size = request.form.get('product-container-size-add')
        product_price = request.form.get('product-price-add')
        product_quantity = request.form.get('product-quantity-add')
        product_status = request.form.get('product-status-add')
        associated_user = request.form.get('user-id')

        # ensure all fields are filled
        if all([product_flavor, product_container_size, product_price, 
                product_quantity, product_status, associated_user
        ]):

            # convert the price and quantity to float and int
            product_price = float(product_price)
            product_quantity = int(product_quantity)

            # update existing product if it exists
            existing_product = Product.query.filter_by(flavor=product_flavor, container_size=product_container_size).first()
            if existing_product:
                existing_product.price = product_price
                existing_product.quantity = product_quantity
                existing_product.status = product_status

                # log the update
                print(f'Updated product: {existing_product}')
        
            else:

                # create a new product object
                new_product = Product(flavor=product_flavor, container_size=product_container_size, 
                                    price=product_price, quantity=product_quantity, 
                                    status=product_status, user_id_add=associated_user)

                # add the new product to the database
                db.session.add(new_product)

                # log the addition
                print(f'Added product: {new_product}')

            # commit the changes
            if db.session.dirty:
                db.session.commit()
            
            # log the action
            new_log = Log(
                action = "Added",
                product = product_flavor,
                user = associated_user
            )
            
            db.session.add(new_log)
            db.session.commit()
            
    return redirect(url_for('inventory.inventory_home'))



# inventory delete endpoint >> TODO: implement disposition!
@inventory.route('/inventory_delete', methods=['GET', 'POST'])
@login_required
def inventory_delete_product():
    
    # check if the request is a POST request
    if request.method == 'POST':

        # extract the product id from the form
        product_id = request.form.get('product-id-delete')
        associated_user = request.form.get('user-id-delete')

        # find the product in the database
        product = Product.query.get(product_id)

        # check if the product exists
        if product:

            # check if the product is not already deleted and the user exists
            if (product.deleted_at is None and associated_user is not None):
                product.deleted_at = datetime.now()
                product.user_id_delete = associated_user
                db.session.commit()

                # TODO: log the deletion
                print(f'Deleted product: {product}')
                
                # log the action
                new_log = Log(
                    action =  "Deleted",
                    product = product.flavor,
                    user = associated_user
                )
                
                db.session.add(new_log)
                db.session.commit()

            else:

                # TODO: log the error / handle the error
                print(f'Product already deleted or user not found: {product.deleted_at, associated_user}')
        else:

            # TODO: log the error / handle the error
            print(f"Product not found: {product}")

    # redirect to the inventory page
    return redirect(url_for('inventory.inventory_home'))


# inventory customer add endpoint
@inventory.route('/inventory_customer_add', methods=['GET', 'POST'])
@login_required
def inventory_add_customer():

    # TODO: implement customer add functionality
    # if request.method == 'POST':

        # # extract the customer data from the form
        # customer_name = request.form.get('customer-name')
        # customer_email = request.form.get('customer-email')
        # customer_phone = request.form.get('customer-phone')
        # customer_address = request.form.get('customer-address')
        # customer_status = request.form.get('customer-status')

    # redirect to the inventory page
    return redirect(url_for('inventory.inventory_home'))