from flask import Blueprint, request, redirect, url_for, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.utils.data import *
from app.models import Product, User, Order, OrderItem, AdminConfig, ProductAllocation, Shipment
from app.extensions import db
from app.utils.order_items import extract_order_items, compare_order_items, create_order_item
from app.utils.checks import check_customer_order_limit
from app.utils.admin_decorator import admin_required
from pprint import pprint
from datetime import datetime, timedelta
from app.endpoints.shipments import create_shipment
from pprint import pprint

# create the order entry form blueprint
orders = Blueprint('orders', __name__)

# inventory home endpoint
@orders.route('/orders', methods=['GET'])
@login_required
def orders_home():

    # fetch any messages from the query string
    msg = request.args.get('msg')
    msg_type = request.args.get('msg_type')
    shipment_id = request.args.get('shipment_id')

    # fetch all orders from the database
    orders = Order.query.all()

    # fetch all products from the database
    products = Product.query.filter_by(deleted_at=None).all()

    # fetch all customers from the database
    customers = User.query.all()

    # fetch supported shipping types and costs from the database
    shipping_types = AdminConfig.query.filter_by(key='supported_shipping_types').first()
    shipping_costs = AdminConfig.query.filter_by(key='supported_shipping_costs').first()

    # parse the orders and customers data into lists of dictionaries
    orders_dict = parse_order_data(orders)
    customers_dict = parse_customer_data(customers)

    # format the date attribute
    for order in orders_dict:
        if order['payment_date']:
            order['payment_date'] = order['payment_date'].strftime("%m/%d/%Y")
        else:
            order['payment_date'] = '-'

        # include the shipment ID
        shipment = Order.query.get(int(order['id'])).shipment
        if shipment:
            order['shipment_id'] = shipment.id

    # dictionary of items to pass to the template
    jinja_vars = {
        'unique_flavors': list(set([product.flavor for product in products])),
        'orders': orders_dict,
        'customers': customers_dict,
        'shipping_types': shipping_types.value.split(',') if shipping_types else None,
        'shipping_costs': shipping_costs.value.split(',') if shipping_costs else None
    }

    # add order_id to dictionary from shipment_id if it exists
    if shipment_id:
        shipment = Shipment.query.get(shipment_id)
        if shipment:
            jinja_vars['shipment_id'] = shipment.id
        else:
            msg = "Shipment not found"

    # if a message was passed, add it to the dictionary
    if msg:
        jinja_vars['msg'] = msg
        jinja_vars['msg_type'] = msg_type

    return render_template('orders/orders.html', **jinja_vars)

# orders update endpoint
@orders.route('/orders_update', methods=['GET', 'POST'])
@login_required
def orders_update_order():
     
    # check if POST request was made
    if request.method == 'POST':

        # initialize message variables
        msg = ''
        msg_type = ''

        # wrap in try-except block to catch any errors
        try:

            pprint(request.form)

            # extract form data
            user_id = request.form.get("order-user-id-update-hidden")
            order_id = request.form.get('order-id-update-hidden')
            shipping_type = request.form.get('shipping-type-update')
            shipping_cost = request.form.get('shipping-cost-update')
            desired_receipt_date = request.form.get("desired-receipt-date-update")
            payment_date = request.form.get('payment-date-update')
            billing_address = request.form.get('billing-address-update')
            order_status = request.form.get('order-status-update')
            order_status_hidden = request.form.get('order-status-update-hidden')
            total_cost = request.form.get('order-total-cost-hidden')
            order_items = extract_order_items(request.form)

            # set the order status to the hidden value if it is empty
            if not order_status:
                order_status = order_status_hidden

            # ensure all fields are filled
            if not all([ order_id, order_status, shipping_type, shipping_cost, desired_receipt_date, 
                    billing_address, total_cost ]):
                return redirect(url_for('orders.orders_home', msg="Missing fields"))
            
            # if the payment date is not empty, convert it to a datetime object
            if payment_date:
                payment_date = datetime.strptime(payment_date, "%Y-%m-%d").strftime("%m/%d/%Y")

            # check if the user has exceeded their order limit
            user = User.query.get(user_id)
            if user:
                customer_limit = check_customer_order_limit(user.status)
                print(f"Customer limit: {customer_limit}")
                if customer_limit < float(total_cost):
                    msg = (f"Order exceeds customer limit (${customer_limit})")
                    return redirect(url_for('orders.orders_home', msg=msg))
            else:
                msg = "User not found"
                return redirect(url_for('orders.orders_home', msg=msg))

            # fetch the order from the database
            order = Order.query.get(order_id)

            # display a message if any of the order attributes have changed
            if any( [
                order.status != (request.form.get('order-status-update') or order_status),
                order.shipping_type != request.form.get('shipping-type-update').lower(),
                order.shipping_cost != float(request.form.get('shipping-cost-update')),
                order.desired_receipt_date.strftime("%m/%d/%Y") != \
                    datetime.strptime(request.form.get('desired-receipt-date-update'), "%m/%d/%Y").strftime("%m/%d/%Y"),
                order.billing_address != request.form.get('billing-address-update'),
                order.total_cost != float(request.form.get('order-total-cost-hidden')),
                payment_date
            ] ):
                msg = "Order updated successfully"
                msg_type = "success"
            else:
                msg = "No changes made"
                msg_type = "info"

            # TODO: update the product allocation status
            
            # update the order object
            order.status = order_status
            order.shipping_type = shipping_type.lower()
            order.shipping_cost = shipping_cost
            order.desired_receipt_date = datetime.strptime(desired_receipt_date, "%m/%d/%Y")
            order.payment_date = datetime.strptime(payment_date, "%m/%d/%Y") if payment_date else None
            order.billing_address = billing_address
            order.total_cost = total_cost

            # get order line-item ids from the database
            order_item_ids = [order_item.id for order_item in order.order_items]

            # construct the line-items from the database
            order_items_db = []
            for order_item_id in order_item_ids:

                # fetch the associated order-item/product from the database
                order_item = OrderItem.query.get(order_item_id)
                product = Product.query.get(order_item.product_id)

                # construct the order-item dictionary from the database
                order_item_db_dict = {
                    key: value for key, value in order_item.__dict__.items() if key != '_sa_instance_state'
                }

                # add product attributes to the order-item dictionary
                order_item_db_dict.update({
                    'flavor': product.flavor,
                    'container_size': product.container_size,
                })

                # push the order-item dictionary to the order-items dictionary
                order_items_db.append(order_item_db_dict)

            # compare each order item from the request to the database
            for i in range(len(order_items)):

                # if order item request list is larger than that in database, add new order items
                if i >= len(order_items_db):

                    # create a newly added order_item
                    inner_msg = create_order_item(order_items[i], order_id)

                    # return with error message if received
                    if inner_msg:
                        return redirect(url_for('orders.orders_home', msg=inner_msg))
                    else:
                        print("New Item Created")
                        continue

                # get the next order item dicts to compare (request vs. database)
                order_item_request = order_items[i]
                order_item_db = order_items_db[i]

                # check if the order items are the same
                relevant_features = ['flavor', 'container_size', 'quantity', 'line_item_cost']
                if not compare_order_items(order_item_request, order_item_db, relevant_features):
                    print("Order items do not match")

                    # fetch the order item from the database
                    order_item = OrderItem.query.get(order_item_db['id'])

                    # fetch the product & product allocation from the database
                    product = Product.query.filter_by(
                        flavor=order_item_request['flavor'], 
                        container_size=order_item_request['container_size'], 
                        deleted_at=None).first()
                    product_allocation = ProductAllocation.query.get(product.allocation.id)

                    if product_allocation:

                        # check if the product id is the same as the order item product id
                        if product.id == order_item.product_id:

                            # change attributes of the order item
                            order_item.quantity = order_item_request['quantity']
                            order_item.line_item_cost = order_item_request['line_item_cost']

                            # update the product/allocation quantity & committed quantity
                            quantity_diff = order_item_request['quantity'] - order_item_db['quantity']
                            product_allocation.adjust_quantity(quantity_diff)

                            print("Order item updated")
                            msg = "Order item updated"

                        else:
                            print("Product ID mismatch")
                            msg = "Product ID mismatch"

                    else:
                        print("Product not found")
                        msg = "Product not found"
                else:
                    print("Order items match")
                    msg = "No changes made" if not msg else msg
                    msg_type = "info" if not msg_type else msg_type

            # delete any order items that weren't passed in the request
            if len(order_items_db) > len(order_items):
                start = len(order_items)
                stop = len(order_items_db)
                for j in range(start, stop, 1):

                    # get order_item id
                    order_item = order_items_db[j]
                    order_item_id = order_item.get('id') if order_item else None

                    # delete order_item, if it exists
                    if order_item_id:
                        order_item = OrderItem.query.get(order_item_id)
                        if order_item:

                            # adjust associated product/product allocation quantities
                            product_allocation = ProductAllocation.query.get(order_item.allocation[0].id)
                            product_allocation.adjust_quantity(-product_allocation.quantity_allocated)

                            db.session.delete(order_item)

                            msg = "Order update successfully"
                            msg_type = "success"

            # commit the changes to the database
            if db.session.dirty:
                db.session.commit()

        except Exception as e: # rollback if an error occurs
            print(e)
            db.session.rollback()

        # redirect back to the order form with a message
        return redirect(url_for('orders.orders_home', msg=msg, msg_type=msg_type))

# orders add endpoint
@orders.route('/orders_add', methods=['GET', 'POST'])
@login_required
def orders_add_order():
    
    # check if POST request was made
    if request.method == 'POST':

        print(request.form)

        # extract form data
        user_id = request.form.get('user-id')
        customer_status = request.form.get('customer-status')
        shipping_type = request.form.get('shipping-type')
        shipping_cost = request.form.get('shipping-cost')
        expected_shipping_date = request.form.get('expected-shipping-date')
        desired_receipt_date = datetime.strptime(request.form.get('desired-receipt-date'), "%Y-%m-%d").strftime("%m/%d/%Y")
        shipping_address = request.form.get('shipping-address')
        billing_address = request.form.get('billing-address')
        order_status = request.form.get('order-status')
        total_cost = request.form.get('total-cost')

        order_items_data = []
        for key in request.form:
            if key.startswith('order_items'):
                index = int(key.split('[')[1].split(']')[0])
                item_key = key.split('[')[2].split(']')[0]
                if len(order_items_data) <= index:
                    order_items_data.append({})
                order_items_data[index][item_key] = request.form.get(key)

        # retrieve the user
        user = User.query.get(user_id)
        if not user:
            msg = "User not found"
            return redirect(url_for('orders.orders_home', msg=msg))

        # ensure all fields are filled
        if not all([user_id, expected_shipping_date, desired_receipt_date, shipping_type,
                    shipping_cost, shipping_address, billing_address, order_status, 
                    total_cost, order_items_data]):
            return redirect(url_for('orders.orders_home', msg="Missing fields"))
        
        # convert date attributes to datetime objects
        try:
            expected_shipping_date = datetime.strptime(expected_shipping_date, "%m/%d/%Y")
            desired_receipt_date = datetime.strptime(desired_receipt_date, "%m/%d/%Y")
            created_at = datetime.strptime(datetime.now().strftime("%m/%d/%Y"), "%m/%d/%Y")
        except ValueError:
            msg = "Invalid date format"
            return redirect(url_for('orders.orders_home', msg=msg))
        
        # convert other attributes to the correct types
        try:
            user_id = int(user_id)
            shipping_cost = float(shipping_cost)
            total_cost = float(total_cost)
        except ValueError:
            msg = "Error with input types"
            return redirect(url_for('orders.orders_home', msg=msg))
        
        # check if the user has exceeded their order limit
        customer_limit = check_customer_order_limit(customer_status)
        if customer_limit < total_cost:
            msg = (f"Order exceeds customer limit (${customer_limit})")
            return redirect(url_for('orders.orders_home', msg=msg))

        # initialize the order object
        new_order = Order(
            user_id=user_id,
            shipping_type=shipping_type,
            shipping_cost=shipping_cost,
            expected_shipping_date=expected_shipping_date,
            desired_receipt_date=desired_receipt_date,
            shipping_address=user.shipping_address,
            billing_address=user.billing_address,
            status=order_status,
            total_cost=total_cost,
            created_at=created_at
        )

        # add the order to the database
        db.session.add(new_order)
        db.session.flush()  # flush to get the order ID

        order_id = new_order.id

    # add order items
    for item_data in order_items_data:
        flavor = item_data.get('flavor')
        container_size = item_data.get('container-size')
        quantity = int(item_data.get('quantity'))
        line_item_cost = float(item_data.get('line-item-cost'))

        # retrieve the product
        product = Product.query.filter_by(flavor=flavor, container_size=container_size, deleted_at=None).first()
        if not product:
            msg = (f"Product with flavor {flavor} and container size {container_size} not found")
            return redirect(url_for('orders.orders_home', msg))

        # check if the quantity is available
        if product.quantity < quantity:
            msg = (f"Not enough stock for product {product.name} ({product.container_size})")
            return redirect(url_for('orders.orders_home', msg))

        # create the order item
        order_item_dict = {
            "flavor": flavor,
            "container_size": container_size,
            "quantity": quantity,
            "line_item_cost": line_item_cost
        }
        inner_msg = create_order_item(order_item_dict, order_id)

        # return with error message if received
        if inner_msg:
            return redirect(url_for('orders.orders_home', msg=inner_msg))
        else:
            print("New Item Created")

    # commit the transaction
    db.session.commit()

    msg = "Order added successfully"

    # create new shipment with order
    create_shipment(new_order.id)

    # redirect back to the order form
    return redirect(url_for('orders.orders_home', msg=msg, msg_type='success'))


# orders delete endpoint
@orders.route('/orders_delete', methods=['GET', 'POST'])
@login_required
def orders_delete_order():
    
        # check if POST request was made
        if request.method == 'POST':

            try:

                # initialize message variable
                msg, msg_type = '', ''
        
                # extract form data
                order_id = request.form.get('order-id-delete')

                # ensure all fields are filled
                if order_id:
        
                    # fetch the order from the database
                    order = Order.query.get(order_id)
        
                    # check if the order exists
                    if order:

                        # fetch the order items from the database
                        order_items = OrderItem.query.filter_by(order_id=order_id).all()

                        # iterate through the order items
                        for order_item in order_items:

                            if order_item.allocation:

                                # fetch the product allocation from the database
                                product_allocation = ProductAllocation.query.get(order_item.allocation[0].id)

                                if product_allocation:
                                    
                                    # update the product allocation & product quantities
                                    product_allocation.adjust_quantity(-product_allocation.quantity_allocated)

                                    # delete the product allocation
                                    db.session.delete(product_allocation)

                                else:
                                    print("Product allocation not found")
                                    return redirect(url_for('orders.orders_home', msg="Product allocation not found"))
        
                        # delete the order from the database
                        db.session.delete(order)
                        db.session.commit()
        
                        # redirect back to the order form
                        msg = "Order deleted successfully"
                        return redirect(url_for('orders.orders_home', msg=msg, msg_type='success'))
        
                    else:
                        msg = "Order not found"
        
                else:
                    msg = "Missing fields"

            except Exception as e:
                print(e)
                msg = e
                db.session.rollback()
    
        return redirect(url_for('orders.orders_home', msg=msg))


# cancel order endpoint
@orders.route('/orders_cancel', methods=['GET', 'POST'])
@login_required
def orders_cancel_order():

    # check if POST request was made
    if request.method == 'POST':

        # initialize message variable
        msg, msg_type = '', ''

        # extract form data
        print(request.form)
        order_id = request.form.get('order-id-cancel')
        user_id = request.form.get('order-user-id-delete')

        # ensure all fields are filled
        if order_id:

            # fetch the order from the database
            order = Order.query.get(order_id)

            # check if the order exists
            if order:

                # update the order status
                order.status = 'cancelled'

                # fetch the order items from the database
                order_items = OrderItem.query.filter_by(order_id=order_id).all()

                # iterate through the order items
                for order_item in order_items:

                    # fetch the product allocation from the database
                    product_allocation = ProductAllocation.query.get(order_item.allocation[0].id)

                    if product_allocation:
                        
                        # update the product allocation & product quantities
                        product_allocation.adjust_quantity(-product_allocation.quantity_allocated)

                        # subtract the line item cost from the order total cost
                        order.total_cost -= order_item.line_item_cost

                        # delete the product allocation
                        db.session.delete(product_allocation)

                    else:
                        print("Product allocation not found")
                        return redirect(url_for('orders.orders_home', msg="Product allocation not found"))

                # update the order status
                order.status = 'cancelled'
                db.session.commit()

                # redirect back to the order form
                msg = "Order cancelled successfully"
                msg_type = 'success'
            
            else:
                msg = "Order not found"

        else:
            msg = "Missing fields"

    return redirect(url_for('orders.orders_home', msg=msg, msg_type=msg_type))



# get available sizes for a flavor endpoint
@orders.route('/orders/fetch_sizes', methods=['GET'])
@login_required
def orders_fetch_sizes():

    # get the flavor from the query string
    flavor = request.args.get('flavor')

    # parse the flavor into a string
    if flavor:
        flavor = str(flavor)
    else:
        return jsonify([])

    # fetch all products from the database with the specified flavor and no deletion date
    products = Product.query.filter_by(flavor=flavor, deleted_at=None).all()

    # extract unique sizes from the products
    sizes = set([product.container_size for product in products])

    # convert the sizes to a list (reverse alphabetical order)
    sizes = sorted(list(sizes), reverse=True)

    # return the sizes as a JSON response
    return jsonify({"sizes": list(sizes)})

# get available stock for a flavor and container size endpoint
@orders.route('/orders/fetch_stock', methods=['GET'])
@login_required
def orders_fetch_stock():

    # get the flavor and container size from the query string
    flavor = request.args.get('flavor')
    container_size = request.args.get('container-size')

    # parse the flavor and container size into strings
    if all([flavor, container_size]):
        flavor = str(flavor)
        container_size = str(container_size)
    else:
        return jsonify([])

    # fetch all products from the database with the specified flavor, container size, and no deletion date
    product = Product.query.filter_by(flavor=flavor, container_size=container_size, deleted_at=None).first()

    # check if the product exists
    if product:
        return jsonify({"stock": product.quantity})

    print(f"Product not found: {flavor}, {container_size}") # TODO: handle this
    return jsonify({"stock": 0})

# get cost for a flavor, container size, and quantity endpoint
@orders.route('/orders/fetch_cost', methods=['GET'])
@login_required
def orders_fetch_cost():

    # get the flavor and container size from the query string
    flavor = request.args.get('flavor')
    container_size = request.args.get('container-size')
    quantity = request.args.get('quantity')

    # if all fields are filled, parse them into the correct types
    if all([flavor, container_size, quantity]):
        flavor = str(flavor)
        container_size = str(container_size)
        quantity = int(quantity)
    else:
        return jsonify({"cost": 0.0})

    # fetch the product from the database
    product = Product.query.filter_by(flavor=flavor, container_size=container_size, deleted_at=None).first()

    # get the cost of the quantity of products
    if product:
        cost = product.price * quantity
    else:
        return jsonify({"cost": 0.0})

    # return the cost as a JSON response
    return jsonify({"cost": cost})
    

# get status of a product endpoint
@orders.route('/orders/fetch_product_status', methods=['GET'])
def orders_fetch_product_status():

    # get the flavor and container size from the query string
    flavor = request.args.get('flavor')
    container_size = request.args.get('container-size')

    # parse the flavor and container size into strings
    if all([flavor, container_size]):
        flavor = str(flavor)
        container_size = str(container_size)
    else:
        return jsonify({"status": "planned"})

    # fetch the product from the database
    product = Product.query.filter_by(flavor=flavor, container_size=container_size, deleted_at=None).first()

    # check if the product exists
    if product:
        return jsonify({"status": product.status})
    else:
        print(f"Product not found: {flavor}, {container_size}") # TODO: handle this

    return jsonify({"status": "planned"})


@orders.route('/orders/fetch_order_info', methods=['GET'])
def orders_fetch_order_info():

    # get the order ID from the query string
    order_id = request.args.get('order_id')

    # parse the order ID into an integer
    if order_id:
        order_id = int(order_id)
    else:
        return jsonify({'error': 'Order not found (missing ID)'})

    # fetch the order from the database
    order = Order.query.get(order_id)

    # check if the order exists
    if order:

        # parse the order data into a dictionary
        order_dict = parse_order_data([order])[0]

        # parse the order items into a list of dictionaries
        if order.order_items[0].allocation and len(order.order_items[0].allocation) > 0:
            order_dict['line_items'] = parse_order_item_data(order.order_items)
        else:
            order_dict['line_items'] = []

        # format the date attributes
        date_attributes = ['order_creation_date', 'expected_shipping_date', 'desired_receipt_date']
        for date_attribute in date_attributes:
            if order_dict[date_attribute]:
                order_dict[date_attribute] = order_dict[date_attribute].strftime("%m/%d/%Y")

        # special format for payment date (YYYY-MM-DD)
        if order_dict['payment_date']:
            order_dict['payment_date'] = order_dict['payment_date'].strftime("%Y-%m-%d")

        # get the associated shipment from the database
        shipment = Shipment.query.filter_by(order_id=order_id).first()

        if shipment:
            order_dict['shipment_id'] = shipment.id

        return jsonify(order_dict)
    else:
        print("Order not found")
        return jsonify({'error': 'Order not found'})