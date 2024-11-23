from flask import Blueprint, request, redirect, url_for, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.utils.data import *
from app.models import Product, User, Order, OrderItem, Shipment
from app.extensions import db
from datetime import datetime, timedelta

# create the order entry form blueprint
orders = Blueprint('orders', __name__)

# inventory home endpoint
@orders.route('/orders', methods=['GET'])
@login_required
def orders_home():

    # fetch all orders from the database
    orders = Order.query.all()

    # fetch all products from the database
    products = Product.query.filter_by(deleted_at=None).all()

    # fetch all customers from the database
    customers = User.query.all()

    # parse the orders and customers data into lists of dictionaries
    orders_dict = parse_order_data(orders)
    customers_dict = parse_customer_data(customers)

    # dictionary of items to pass to the template
    jinja_vars = {
        'unique_flavors': list(set([product.flavor for product in products])),
        'orders': orders_dict,
        'customers': customers_dict
    }

    return render_template('orders/orders.html', **jinja_vars)

# orders update endpoint
@orders.route('/orders_update', methods=['GET', 'POST'])
@login_required
def orders_update_order():
     
    # check if POST request was made
    if request.method == 'POST':
         
        # extract form data
        order_id = request.form.get('order-id')
        customer_name = request.form.get('customer-name')
        customer_status = request.form.get('customer-status')
        shipping_address = request.form.get('shipping-address')
        shipping_type = request.form.get('shipping-type')
        shipping_cost = request.form.get('shipping-cost')
        billing_address = request.form.get('billing-address')
        total_cost = request.form.get('total-cost')

        # ensure all fields are filled
        if all([ order_id, customer_name, customer_status, shipping_address, 
                shipping_type, shipping_cost, billing_address, total_cost ]):
            
            # fetch the order from the database
            order = Order.query.get(order_id)
            
            # update the order object
            order.customer_name = customer_name
            order.customer_status = customer_status
            order.shipping_address = shipping_address
            order.shipping_type = shipping_type
            order.shipping_cost = shipping_cost
            order.billing_address = billing_address
            order.total_cost = total_cost

            # commit the changes to the database
            db.session.commit()

            # redirect back to the order form
            return redirect(url_for('orders.orders_home'))

# orders add endpoint
@orders.route('/orders_add', methods=['GET', 'POST'])
@login_required
def orders_add_order():
    
    # check if POST request was made
    if request.method == 'POST':

        print(request.form)

        # return redirect(url_for('orders.orders_home'))

        # extract form data TODO: fix this
        user_id = request.form.get('user-id')
        shipping_type = request.form.get('shipping-type')
        shipping_cost = request.form.get('shipping-cost')
        shipping_date = request.form.get('shipping-date')
        shipping_address = request.form.get('shipping-address')
        billing_address = request.form.get('billing-address')
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
            print("User not found", "error")
            return redirect(url_for('orders.orders_home'))

        # ensure all fields are filled
        if not all([user_id, shipping_date, shipping_type, shipping_cost, 
                    shipping_address, billing_address, total_cost, order_items_data]):
            print("Missing fields")
            return redirect(url_for('orders.orders_home'))
        
        # convert shipping date to a datetime object
        try:
            shipping_date = datetime.strptime(shipping_date, "%m/%d/%Y")
        except ValueError:
            print("Invalid date format")
            return redirect(url_for('orders.orders_home'))
        
        print(f"Extracted Data: {user_id}, {shipping_date}, {shipping_type}, {shipping_cost}, {total_cost}, {order_items_data}")
        # return redirect(url_for('orders.orders_home'))

        # initialize the order object
        new_order = Order(
            user_id=user_id,
            shipping_type=shipping_type,
            shipping_cost=shipping_cost,
            shipping_date=shipping_date,
            shipping_address=user.shipping_address,
            billing_address=user.billing_address,
            total_cost=total_cost
        )

        # add the order to the database
        db.session.add(new_order)
        db.session.flush()  # flush to get the order ID

    # add order items
    for item_data in order_items_data:
        flavor = item_data.get('flavor')
        container_size = item_data.get('container-size')
        quantity = int(item_data.get('quantity'))
        line_item_cost = float(item_data.get('line-item-cost'))

        # retrieve the product
        product = Product.query.filter_by(flavor=flavor, container_size=container_size).first()
        if not product:
            print(f"Product with flavor {flavor} and container size {container_size} not found", "error")
            return redirect(url_for('orders.orders_home'))

        # check if the quantity is available
        if product.quantity < quantity:
            print(f"Not enough stock for product {product.name} ({product.container_size})", "error")
            return redirect(url_for('orders.orders_home'))

        # update the product quantity
        product.quantity -= quantity

        # create the order item
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=quantity,
            line_item_cost=line_item_cost
        )
        db.session.add(order_item)

    # commit the transaction
    db.session.commit()

    print("Order added successfully", "success")

    # redirect back to the order form
    return redirect(url_for('orders.orders_home'))


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

    print("Product not found")
    return jsonify({"stock": 0})

# get cost for a flavor, container size, and quantity endpoint
@orders.route('/orders/fetch_cost', methods=['GET'])
@login_required
def orders_fetch_cost():

    # get the flavor and container size from the query string
    flavor = request.args.get('flavor')
    container_size = request.args.get('container-size')
    quantity = request.args.get('quantity')

    # print(flavor, container_size, quantity)

    # if all fields are filled, parse them into the correct types
    if all([flavor, container_size, quantity]):
        flavor = str(flavor)
        container_size = str(container_size)
        quantity = int(quantity)
    else:
        return jsonify({"cost": 0.0})

    # fetch the product from the database
    product = Product.query.filter_by(flavor=flavor, container_size=container_size).first()

    # get the cost of the quantity of products
    if product:
        cost = product.price * quantity
    else:
        return jsonify({"cost": 0.0})

    # return the cost as a JSON response
    return jsonify({"cost": cost})
    
    
