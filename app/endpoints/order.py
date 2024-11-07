from flask import Blueprint, request, redirect, url_for, render_template, jsonify
from app.utils.data import *
from app.models import Product, User, Order, OrderItem
from config.config import db

# create the order entry form blueprint
orders = Blueprint('orders', __name__)

# inventory home endpoint
@orders.route('/orders', methods=['GET'])
def orders_home():

    # fetch all orders from the database
    orders = Order.query.all()

    # fetch all products from the database
    products = Product.query.all()

    # fetch all customers from the database (non-admin users)
    customers = User.query.filter_by(is_admin=False).all()

    # parse the product, order, and customers data into lists of dictionaries
    # products_dict = parse_product_data(products)
    orders_dict = parse_order_data(orders)
    customers_dict = parse_customer_data(customers)

    # dictionary of items to pass to the template
    jinja_vars = {
        # 'products': products_dict,
        'unique_flavors': list(set([product.flavor for product in products])),
        'orders': orders_dict,
        'customers': customers_dict
    }

    return render_template('orders/orders.html', **jinja_vars)

# orders update endpoint
@orders.route('/orders_update', methods=['GET', 'POST'])
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
def orders_add_order():
    
    # check if POST request was made
    if request.method == 'POST':

        # extract form data TODO: fix this
        customer_name = request.form.get('customer-name')
        customer_status = request.form.get('customer-status')
        shipping_address = request.form.get('shipping-address')
        shipping_type = request.form.get('shipping-type')
        shipping_cost = request.form.get('shipping-cost')
        billing_address = request.form.get('billing-address')
        total_cost = request.form.get('total-cost')

        # ensure all fields are filled
        if all([ customer_name, customer_status, shipping_address,
                shipping_type, shipping_cost, billing_address, total_cost ]):
                    
                # initialize the order object
                new_order = Order(
                    customer_name=customer_name,
                    customer_status=customer_status,
                    shipping_address=shipping_address,
                    shipping_type=shipping_type,
                    shipping_cost=shipping_cost,
                    billing_address=billing_address,
                    total_cost=total_cost
                )
    
                # add the order to the database
                db.session.add(new_order)
                db.session.commit()
    
                # redirect back to the order form
                return redirect(url_for('orders.orders_home'))

    return render_template('orders/orders.html')

# get available sizes for a flavor endpoint
@orders.route('/orders/get_sizes', methods=['GET'])
def orders_get_sizes():

    # get the flavor from the query string
    flavor = request.args.get('flavor')

    # parse the flavor into a string
    if flavor:
        flavor = str(flavor)
    else:
        return jsonify([])

    # fetch all products from the database
    products = Product.query.filter_by(flavor=flavor).all()

    # extract unique sizes from the products
    sizes = set([product.container_size for product in products])

    # convert the sizes to a list (reverse alphabetical order)
    sizes = sorted(list(sizes), reverse=True)

    # return the sizes as a JSON response
    return jsonify({"sizes": list(sizes)})
    
    
