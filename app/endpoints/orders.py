from flask import Blueprint, request, redirect, url_for, render_template, flash
from app.models import Product, User, OrderItem, Order, Customer
from flask_login import current_user
from app.utils.data import *
from config.config import db
from datetime import datetime

# create the inventory management blueprint
orders = Blueprint('orders', __name__)

@orders.route('/orders', methods=['GET'])
def orders_home():
    
    # get all products from the database
    customers = Customer.query.all()
    orders = Order.query.all()

    # parse the product data into a dictionary
    customers_dict = parse_customer_data(customers)
    orders_dict = parse_order_data(orders)

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
        customer_id = request.form['customer-name'] # using the ID we can get the name, since IDs are unique
        flavor = request.form['flavor']
        size = int(request.form['size'])
        quantity = int(request.form['product-quantity'])
        cost = float(request.form['cost'])
        shipping_type = request.form['shipping-type']
        shipping_date = datetime.strptime(request.form['shipping-date'], '%m/%d/%Y').date()
        shipping_cost = float(request.form['shipping-cost'])
        
        # Ensure all required fields are filled
        if customer_id and flavor and size and quantity and cost and shipping_type and shipping_date and shipping_cost:    
            # query database for the flavor
            product = Product.query.filter_by(flavor=flavor).first()
            
            if product is None: # checks if flavor exists
                print(f"The flavor {flavor} does not exist.", 404)
                return redirect(url_for('orders.orders_home'))
            
            # TODO: Right now, product does not have a size attribute, need to add that in future
            # if product.size != size: # checks if the container size exists
            #     print(f"This size {size} for flavor {flavor} does not exist.", 404)
            
            if product.quantity < quantity: # checks if flavor has enough stock
                print(f"Quantity requested exceeds available invenotry for {flavor}. In stock: {product.quantity}", 404)
                return redirect(url_for('orders.orders_home'))
            
            # calculate total cost of order 
            # TODO: Change to product.size once size attribute gets added to product
            total_cost = size * quantity
            
            # create an order item, update new stock, add order item to order
            # order_item = OrderItem(order=new_order, product=product, quantity = quantity)
            # new_order.order_items.append(order_item)
            
            # Retrieve the  customer with the customer id input
            customer = Customer.query.filter_by(id=customer_id).first()
            
            # Create a new order
            total_order = Order(
                user_id=current_user.get_id(),
                customer_name=customer.name,
                customer_status=customer.status,
                shipping_address=customer.shipping_address,
                shipping_type=shipping_type,
                shipping_cost=shipping_cost,
                billing_address=customer.billing_address,
                total_cost=total_cost
            )
            
            # Create a order item object (a singular unit inside of an order), pointing it to total_order
            order_item = OrderItem(
                order=total_order,
                product_id=product.id,
                quantity=quantity,
                shipping_date=shipping_date
            )
            
            # Add the new order to the database
            db.session.add(total_order)
            db.session.commit()
            
            # update stock for product
            product.quantity -= quantity

            # Log the addition
            print(f'Added order: {total_order}')

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