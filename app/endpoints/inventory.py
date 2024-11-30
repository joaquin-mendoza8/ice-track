from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required
from app.utils.data import *
from app.utils.fetch_settings import fetch_autosignoff_interval, \
    fetch_supported_container_sizes, fetch_supported_flavors
from app.models import Product, User , Log, ProductAllocation
from app.extensions import db
from datetime import datetime

# create the inventory management blueprint
inventory = Blueprint('inventory', __name__) # TOO: set prefix to '/inventory'

# template paths

# ROUTES

# inventory home endpoint
@inventory.route('/inventory', methods=['GET'])
@login_required
def inventory_home():

    # check if msg/msg_type were passed
    msg = request.args.get('msg')
    msg_type = request.args.get('msg_type')

    # check if filter key was passed
    filter_key = request.args.get('filter')

    # get all products from the database
    products = Product.query.filter_by(deleted_at=None).all()

    # get all product allocations from the database
    allocations = ProductAllocation.query.all()

    # if filter key is passed, sort by that key
    if filter_key:
        products = sorted(products, key=lambda x: getattr(x, filter_key))

    # fetch the supported container sizes from the database
    container_sizes = fetch_supported_container_sizes()

    # fetch the supported flavors from the database
    supported_flavors = fetch_supported_flavors()

    # parse the product data into a dictionary
    products_dict = parse_product_data(products)

    # parse the product allocations into a dictionary
    allocations_dict = parse_product_allocation_data(allocations)
    
    # fetch all logs from the database
    logs = Log.query.order_by(Log.timestamp.desc()).all()

    # dictionary of items to pass to the template
    jinja_vars = {
        'products': products_dict,
        'logs' : logs,
        'supported_container_sizes': container_sizes,
        'supported_flavors': supported_flavors,
        'allocations': allocations_dict
    }

    if msg:
        jinja_vars.update({"msg": msg})
    if msg_type:
        jinja_vars.update({"msg_type": msg_type})

    return render_template('inventory/inventory.html', **jinja_vars)


# inventory update endpoint
@inventory.route('/inventory_update', methods=['GET', 'POST'])
@login_required
def inventory_update_product():
    
    # check if the form was submitted
    if request.method == 'POST':

        try:

            msg, msg_type = '', ''

            # extract form data
            product_id = request.form.get('product-id')
            product_flavor = request.form.get('product-flavor')
            product_container_size = request.form.get('product-container-size')
            product_price = request.form.get('product-price')
            product_quantity = request.form.get('product-quantity')
            product_status = request.form.get('product-status')
            product_dock_date = request.form.get('product-dock-date')

            # ensure all fields are filled
            if all([product_id, product_flavor, product_container_size,
                    product_price, product_quantity, product_status,
                    product_dock_date]):
                    
                # find the product in the database
                product = Product.query.get(product_id)

                # if product exists, update it
                if product:

                    # check if none of the fields are different
                    if not any ([
                            product.flavor != product_flavor,
                            product.container_size != product_container_size,
                            product.price != float(product_price),
                            product.quantity != int(product_quantity),
                            product.status != product_status,
                            product.dock_date != datetime.strptime(product_dock_date, '%m/%d/%Y')
                    ]):
                        
                        # log the error
                        print("No changes detected")
                        msg = "No changes detected"
                        msg_type = "info"
                        return redirect(url_for('inventory.inventory_home', msg=msg, msg_type=msg_type))
                    
                    # check if any of the fields are less than or equal to zero
                    if any([
                            float(product_price) <= 0,
                            int(product_quantity) <= 0
                    ]):
                        
                        # log the error
                        print("Price and quantity must be greater than zero")
                        msg = "Price and quantity must be greater than zero"
                        return redirect(url_for('inventory.inventory_home', msg=msg, msg_type=msg_type))

                    # update the product fields
                    product.flavor = product_flavor
                    product.container_size = product_container_size
                    product.price = product_price
                    product.quantity = product_quantity
                    product.status = product_status
                    product.dock_date = datetime.strptime(product_dock_date, '%m/%d/%Y')

                    # commit the changes
                    db.session.commit()

                    # log the success
                    msg = "Product updated successfully"
                    msg_type = "success"

                else:

                    # log the error
                    print("Product not found")
                    msg = "Product not found"

            else:

                # log the error
                print("Missing fields")
                msg = "Missing fields"

        except Exception as e:
            print(e)
            msg = e
            db.session.rollback()

    # redirect to the inventory page
    return redirect(url_for('inventory.inventory_home', msg=msg, msg_type=msg_type))


# inventory add endpoint
@inventory.route('/inventory_add', methods=['GET', 'POST'])
@login_required
def inventory_add_product():
    if request.method == 'POST':

        try:

            msg, msg_type = '', ''

            # extract the product data from the form
            product_flavor = request.form.get('product-flavor-add')
            product_container_size = request.form.get('product-container-size-add')
            product_price = request.form.get('product-price-add')
            product_quantity = request.form.get('product-quantity-add')
            product_status = request.form.get('product-status-add')
            product_dock_date = request.form.get('product-dock-date-add')
            associated_user = request.form.get('user-id')

            # ensure all fields are filled
            if all([product_flavor, product_container_size, product_price, 
                    product_dock_date, product_quantity, product_status, associated_user
            ]):

                # convert the types of price, quantity and dock date
                product_price = float(product_price)
                product_quantity = int(product_quantity)
                product_dock_date = datetime.strptime(product_dock_date, '%m/%d/%Y')

                # update existing product if it exists (removed this)
                # check if product already exists
                existing_product = Product.query.filter_by(flavor=product_flavor, container_size=product_container_size, deleted_at=None).first()
                if existing_product:
                    # existing_product.price = product_price
                    # existing_product.quantity = product_quantity
                    # existing_product.status = product_status
                    # existing_product.dock_date = product_dock_date

                    # # log the update
                    # print(f'Updated product: {existing_product}')
                    # msg = "Updated product successfully"
                    # msg_type = "success"
                    # log the error
                    print("Product already exists")
                    msg = "Product already exists"
            
                else:

                    # create a new product object
                    new_product = Product(flavor=product_flavor, container_size=product_container_size, 
                                        price=product_price, quantity=product_quantity, 
                                        status=product_status, user_id_add=associated_user, 
                                        dock_date=product_dock_date, created_at=datetime.now())

                    # add the new product to the database
                    db.session.add(new_product)

                    # log the addition
                    print(f'Added product: {new_product}')
                    msg = "Added product successfully"
                    msg_type = "success"
                
                    # log the action
                    new_log = Log(
                        action = "added",
                        product = product_flavor,
                        container_size = product_container_size,
                        user_id = associated_user
                    )
                
                db.session.add(new_log)
                db.session.commit()

            else:

                # log the error
                print("Missing fields")
                msg = "Missing fields"

        except Exception as e:
            print(e)
            msg = e
            db.session.rollback()
            
    return redirect(url_for('inventory.inventory_home', msg=msg, msg_type=msg_type))



# inventory delete endpoint >> TODO: implement disposition!
@inventory.route('/inventory_delete', methods=['GET', 'POST'])
@login_required
def inventory_delete_product():
    
    # check if the request is a POST request
    if request.method == 'POST':

        try:

            msg, msg_type = '', ''

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

                    # log the deletion
                    print(f"Deleted product: {product}")
                    msg = "Deleted product successfully"
                    msg_type = "success"
                    
                    # log the action
                    new_log = Log(
                        action =  "deleted",
                        product = product.flavor,
                        container_size = product.container_size,
                        user_id = associated_user
                    )
                    
                    db.session.add(new_log)
                    db.session.commit()

                else:

                    # log the error
                    print(f"Product already deleted or user not found: {product.deleted_at, associated_user}")
                    msg = "Product already deleted or user not found"
            else:

                # log the error
                print(f"Product not found: {product}")
                msg = "Product not found"
        
        except Exception as e:
            print(e)
            msg = e
            db.session.rollback()

    # redirect to the inventory page
    return redirect(url_for('inventory.inventory_home'))

@inventory.route('/inventory_add', methods=['GET', 'POST'])
def inventory_add_product():

    # check if the request is a POST request
    if request.method == 'POST':

        # extract the product data from the form
        product_flavor = request.form['product-flavor']
        product_price = request.form['product-price']
        product_quantity = request.form['product-quantity']
        product_status = request.form['product-status']
        associated_user = request.form['user-id']

        # ensure all fields are filled "add container_size", "add product status"
        if (product_flavor and product_price and product_quantity):

            # create a new product object
            new_product = Product(flavor=product_flavor, price=product_price, quantity=product_quantity, 
                                  status=product_status, user_id_add=associated_user)

            # add the new product to the database
            db.session.add(new_product)
            db.session.commit()

            # log the addition
            print(f'Added product: {new_product}')

    # redirect to the inventory page
    return redirect(url_for('inventory.inventory_home'))
