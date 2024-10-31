from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.data import *
from app.models import Product
#from app.models import Order
#from app.models import Customer
from config.config import db
#from datetime import datetime

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
def orders():
        return render_template('orders.html')
    
@inventory.route('/shipments', methods=['GET'])
def shipments():
        return render_template('shipments.html')

@inventory.route('/tickets', methods=['GET'])
def tickets():
        return render_template('tickets.html')
    
@inventory.route('/inventory_add', methods=['GET', 'POST'])
def inventory_add_product():

    # check if the request is a POST request
    if request.method == 'POST':

        # extract the product data from the form
        product_flavor = request.form['product-flavor']
        product_price = request.form['product-price']
        product_quantity = request.form['product-quantity']

        # ensure all fields are filled
        if (product_flavor and product_price and product_quantity):

            # create a new product object
            new_product = Product(flavor=product_flavor, price=product_price, quantity=product_quantity)

            # add the new product to the database
            db.session.add(new_product)
            db.session.commit()

            # log the addition
            print(f'Added product: {new_product}')

    # redirect to the inventory page
    return redirect(url_for('inventory.inventory_home'))

@inventory.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        # Extract the form data from the modal form
        flavor = request.form['flavor']
        size = request.form['size']
        quantity = request.form['product-quantity']
        cost = request.form['cost']
        shipping_type = request.form['shipping-type']
        shipping_date = request.form['shipping-date']
        shipping_cost = request.form['shipping-cost']
        
        shipping_date = datetime.strptime(shipping_date, '%m/%d/%Y').date()

        # Ensure all required fields are filled
        if flavor and size and quantity and cost and shipping_type and shipping_date and shipping_cost:
            # Create a new product object
            new_product = Order(
                flavor=flavor,
                size=size,
                quantity=quantity,
                cost=cost,
                shipping_type=shipping_type,
                shipping_date=shipping_date,
                shipping_cost=shipping_cost
            )

            # Add the new product to the database
            db.session.add(new_product)
            db.session.commit()

            # Log the addition
            print(f'Added product: {new_product}')

            # Redirect or render as needed
            return redirect(url_for('inventory.orders'))

    return render_template('orders.html')  # or the appropriate template

@inventory.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        # Extract the form data from the modal form
        customer_name = request.form['customer-name']
        status = request.form['customer-status']
        shipping_address = request.form['shipping-address']
        billing_address = request.form['billing-address']

        # Ensure all required fields are filled
        if customer_name and status and shipping_address and billing_address:
            # Create a new product object
            new_customer = Customer(
                name=customer_name,
                status=status,
                shipping_address=shipping_address,
                billing_address=billing_address,
            )

            # Add the new product to the database
            db.session.add(new_customer)
            db.session.commit()

            # Log the addition
            print(f'Added product: {new_customer}')

            # Redirect or render as needed
            return redirect(url_for('inventory.orders'))

    return render_template('orders.html')  # or the appropriate template




