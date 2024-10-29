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
    customer_name = request.form['customer-name']
    customer_status = request.form['customer-status']
    shipping_address = request.form['shipping-address']
    shipping_type = request.form['shipping-type']
    shipping_cost = float(request.form['shipping-cost'])
    billing_address = request.form['billing-address']
    total_cost = float(request.form['total-cost'])

    new_order = Order(
        customer_name=customer_name,
        customer_status=customer_status,
        shipping_address=shipping_address,
        shipping_type=shipping_type,
        shipping_cost=shipping_cost,
        billing_address=billing_address,
        total_cost=total_cost
    )

    line_items = request.form.getlist('line-items')
    for item in line_items:
        flavor = item['flavor']
        size = item['size']
        quantity = item['quantity']
    
    product = Product.query.filter_by(flavor=flavor, size=size).first()
    if product is None:
        return "This product does not exist", 404
    
    if product.quantity < quantity:
        return f"Quantity requested exceeds available invenotry for {flavor}. In stock: {product.quantity}", 400
    
    order_item = OrderItem(order=new_order, product=product, quantity = quantity)
    product.quantity -= quantity
    new_order.order_items.append(order_item)

    db.session.add(new_order)
    db.session.commit()
    return redirect(url_for('order.order_home'))


    
    
