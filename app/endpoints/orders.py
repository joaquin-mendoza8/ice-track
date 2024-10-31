from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.data import *
from app.models import Product
from app.models import Order
from app.models import Customer
from config.config import db
from datetime import datetime

# create the inventory management blueprint
orders = Blueprint('orders', __name__)

@orders.route('/orders', methods=['GET'])
def orders_home():
    # check if filter key was passed
    filter_key = request.args.get('filter')

    # get all products from the database
    customers = Customer.query.all()
    orders = Order.query.all()

    # if filter key is passed, sort by that key
    if filter_key:
        orders = sorted(orders, key=lambda x: getattr(x, filter_key))
        customers = sorted(customers, key=lambda x: getattr(x, filter_key))

    # parse the product data into a dictionary
    customers_dict = parse_customers_data(customers)
    orders_dict = parse_orders_data(orders)

    # dictionary of items to pass to the template
    jinja_vars = {
        'orders': orders_dict,
        'customers': customers_dict
    }
    
    return render_template('orders.html', **jinja_vars)
    
@orders.route('/add_order', methods=['GET', 'POST'])
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
            
            # Create a new order object
            new_order = Order(
                flavor=flavor,
                size=size,
                quantity=quantity,
                cost=cost,
                shipping_type=shipping_type,
                shipping_date=shipping_date,
                shipping_cost=shipping_cost
            )

            # Add the new product to the database
            db.session.add(new_order)
            db.session.commit()

            # Log the addition
            print(f'Added order: {new_order}')

        # Redirect or render as needed
        return redirect(url_for('orders.orders_home'))

@orders.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        
        # Extract the form data from the modal form
        customer_name = request.form['customer-name']
        status = request.form['customer-status']
        shipping_address = request.form['shipping-address']
        billing_address = request.form['billing-address']

        # Ensure all required fields are filled
        if customer_name and status and shipping_address and billing_address:
            # Create a new customer object
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
            print(f'Added customer: {new_customer}')

    # Redirect or render as needed
    return redirect(url_for('orders.orders_home'))