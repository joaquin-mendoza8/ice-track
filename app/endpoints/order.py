from flask import Blueprint, request, redirect, url_for, render_template
from app.utils.data import *
from app.models import Product, User, Order, OrderItem
from config.config import db

# create the order entry form blueprint
order = Blueprint('order', __name__)

# inventory home endpoint
@order.route('/order', methods=['GET'])
def order_home():
    return render_template('order.html')

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


    
    
