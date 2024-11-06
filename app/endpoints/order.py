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

    # parse the product/order data into a dictionary
    products_dict = parse_product_data(products)
    orders_dict = parse_order_data(orders)


    # dictionary of items to pass to the template
    jinja_vars = {
        'products': products_dict,
        'orders': orders_dict
    }

    return render_template('orders.html', **jinja_vars)

# inventory add endpoint
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
        if (
            customer_name and customer_status and shipping_address and
            shipping_type and shipping_cost and billing_address and total_cost
        ):
                    
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

    return render_template('orders.html')

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

    print("FLAVOR RECEIVED:", flavor)
     
    # # get the product id from the query string
    # product_id = request.args.get('product-id')

    # # get the flavor from the product
    # flavor = Product.query.get(product_id).flavor

    # fetch all products from the database
    products = Product.query.filter_by(flavor=flavor).all()

    # extract unique sizes from the products
    sizes = set([product.size for product in products])

    # return the sizes as a JSON response
    return jsonify(list(sizes))

'''
def create_order():
    # retrieve the order detail from order entry form
    customer_name = request.form['customer-name']
    customer_status = request.form['customer-status']
    shipping_address = request.form['shipping-address']
    shipping_type = request.form['shipping-type']
    shipping_cost = float(request.form['shipping-cost'])
    billing_address = request.form['billing-address']
    total_cost = shipping_cost

    # read lines from the form, specifically flavor, size, and quantity
    line_items = request.form.getlist('line-items')
    for item in line_items:
        flavor = item['flavor']
        size = item['size']
        quantity = item['quantity']

        # query database for the flavor
        product = Product.query.filter_by(flavor=flavor).first()
        if product is None: # checks if flavor exists
            return f"The flavor {flavor} does not exist.", 404
        
        if product.size != size: # checks if the container size exists
            return f"This size {size} for flavor {flavor} does not exist.", 404
        
        if product.quantity < quantity: # checks if flavor is in stock
            return f"Quantity requested exceeds available invenotry for {flavor}. In stock: {product.quantity}", 400
        
        # calculate total cost of order
        line_item_cost = product.size * quantity
        total_cost += line_item_cost

        # create an order item, update new stock, add order item to order
        order_item = OrderItem(order=new_order, product=product, quantity = quantity)
        product.quantity -= quantity
        new_order.order_items.append(order_item)

    #initialize Order object from extracted details above
    new_order = Order(
        customer_name=customer_name,
        customer_status=customer_status,
        shipping_address=shipping_address,
        shipping_type=shipping_type,
        shipping_cost=shipping_cost,
        billing_address=billing_address,
        total_cost=total_cost
    )

    # updates database and goes back to order form
    db.session.add(new_order)
    db.session.commit()
    return redirect(url_for('order.order_home'))
'''

    
    
