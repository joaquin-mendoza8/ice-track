from flask import Blueprint, request, redirect, url_for, render_template, jsonify
from flask_login import login_required
from app.utils.data import *
from app.utils.fetch_settings import fetch_autosignoff_interval, \
    fetch_supported_container_sizes, fetch_supported_flavors
from app.utils.checks import update_committed_quantities, check_inventory_update
from app.models import Product, User , Log, ProductAllocation, Shipment
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

    # update the committed quantity for each product
    update_committed_quantities_msg = update_committed_quantities(products)

    # if filter key is passed, sort by that key
    if filter_key:
        products = sorted(products, key=lambda x: getattr(x, filter_key))

    # fetch the supported container sizes from the database
    container_sizes = fetch_supported_container_sizes()

    # fetch the supported flavors from the database
    supported_flavors = fetch_supported_flavors()

    # parse the product data into a dictionary
    products_dict = parse_product_data(products)

    # format product dock dates
    for product in products_dict:
        product['dock_date_display'] = product['dock_date'].strftime('%m/%d/%Y') # format for display
        product['dock_date'] = product['dock_date'].strftime('%Y-%m-%d')    # format for input type=date

    # parse the product allocations into a dictionary
    allocations_dict = parse_product_allocation_data(allocations)

    # parse the schedule data into a dictionary (planned products)
    planned_products = [product for product in products if product.status == "planned"]
    schedule_dict = parse_schedule_data(planned_products)

    # sort the schedule by dock date
    schedule_dict = sorted(schedule_dict, key=lambda x: x['dock_date'])
    
    # fetch all logs from the database
    logs = Log.query.order_by(Log.timestamp.desc()).all()

    # dictionary of items to pass to the template
    jinja_vars = {
        'products': products_dict,
        'logs' : logs,
        'supported_container_sizes': container_sizes,
        'supported_flavors': supported_flavors,
        'allocations': allocations_dict,
        'schedule': schedule_dict,
    }

    # check if update committed quantities message exists
    if update_committed_quantities_msg:
        jinja_vars.update({"msg": update_committed_quantities_msg})
    else:
        # add the message and message type to the dictionary if they exist
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
            product_dock_date = datetime.strptime(request.form.get('product-dock-date'), '%Y-%m-%d').strftime('%m/%d/%Y')
                    
            # find the product in the database
            product = Product.query.get(product_id)

            request_data = {
                "product_id": product_id,
                "product_flavor": product_flavor,
                "product_container_size": product_container_size,
                "product_price": product_price,
                "product_quantity": product_quantity,
                "product_status": product_status,
                "product_dock_date": product_dock_date
            }

            # run checks on the product fields and update if necessary
            check_msg, check_msg_type = check_inventory_update(product, request_data)

            # if check message exists, set it as the message
            if check_msg and check_msg_type:
                msg = check_msg
                msg_type = check_msg_type
                print(msg, msg_type)
                return redirect(url_for('inventory.inventory_home', msg=msg, msg_type=msg_type))
            
            # if the status is changed to actual, check if the product already exists
            if product.status != product_status and product_status == "actual":

                # check if there's an existing product with an 'actual' status
                existing_product = Product.query.filter_by(
                    flavor=product_flavor,
                    container_size=product_container_size,
                    price=product_price,
                    status="actual",
                    deleted_at=None).first()
                
                # check if the product exists
                if existing_product:

                    # add the planned product quantity to the existing product
                    existing_product.quantity += int(product_quantity)

                    # delete the planned product
                    db.session.delete(product)

                    # log the success
                    msg = "Planned product(s) added to existing product successfully"
                    msg_type = "success"

                    # commit the changes
                    db.session.commit()
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
            return redirect(url_for('inventory.inventory_home', msg=msg, msg_type=msg_type))

        except Exception as e:
            print(e)
            msg = e
            db.session.rollback()


# inventory add endpoint
@inventory.route('/inventory_add', methods=['POST'])
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
            if not all([product_flavor, product_container_size, product_price, 
                    product_dock_date, product_quantity, product_status, associated_user
            ]):
                # log the error
                print("Missing fields")
                msg = "Missing fields"
                return redirect(url_for('inventory.inventory_home', msg=msg))

            # convert the types of price, quantity and dock date
            try:
                product_price = float(product_price)
                product_quantity = int(product_quantity)
                product_dock_date = datetime.strptime(product_dock_date, "%Y-%m-%d") if product_dock_date else None
            except Exception as e:
                msg = e
                print("Error converting types")
                return redirect(url_for('inventory.inventory_home', msg=msg))

            # check if product already exists
            existing_product = Product.query.filter_by(
                                            flavor=product_flavor, 
                                            container_size=product_container_size,
                                            price=product_price, 
                                            deleted_at=None).first()

            # if product exists and the status is actual, log the error
            if existing_product and existing_product.status == product_status:
                
                # log the error
                print("Product already exists")
                msg = "Product already exists"
                return redirect(url_for('inventory.inventory_home', msg=msg))

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
        
            # log the action (unless product is from a test user)
            if not (int(associated_user) == 999 or product_flavor == "test"):
                new_log = Log(
                    action = "added",
                    product = product_flavor,
                    container_size = product_container_size,
                    user_id = associated_user
                )
            
                db.session.add(new_log)

            db.session.commit()

            return redirect(url_for('inventory.inventory_home', msg=msg, msg_type=msg_type))

        except Exception as e:
            print(e)
            msg = e
            db.session.rollback()


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
                    
                    # log the action (unless product is from a test user)
                    if not (int(associated_user) == 999 or product.flavor == "test"):
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
    return redirect(url_for('inventory.inventory_home', msg=msg, msg_type=msg_type))


@inventory.route('/inventory_update_allocation', methods=['GET'])
@login_required
def inventory_update_allocation():

    try:

        msg, msg_type = '', ''

        # extract the allocation data from the form
        allocation_id = request.args.get('id')
        allocation_disposition = request.args.get('disposition')

        # ensure all fields are filled
        if allocation_id and allocation_disposition:

            # find the allocation in the database
            allocation = ProductAllocation.query.get(allocation_id)

            # check if the allocation exists
            if allocation:

                # update the allocation disposition
                allocation.disposition = allocation_disposition

                # commit the changes
                db.session.commit()

                # return the success message
                msg = "Allocation updated successfully"
                return jsonify({"msg": msg, "msg_type": "success"})

            else:

                # log the error
                print("Allocation not found")
                msg = "Allocation not found"

        else:

            # log the error
            print("Missing fields")
            msg = "Missing fields"

    except Exception as e:
        print(e)
        msg = e
        db.session.rollback()

    # return the error message
    return jsonify({"msg": msg, "msg_type": "error"})
