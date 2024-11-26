from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required
from app.utils.data import *
from app.models import Product, User, Order, OrderItem, Shipment
from app.extensions import db
from datetime import datetime, timedelta

# create the shipments blueprint
shipments = Blueprint('shipments', __name__)

# shipments home endpoint
@shipments.route('/shipments', methods=['GET'])
@login_required
def shipments_home():

    # fetch all shipments from database
    shipments = Shipment.query.all()

    #parse the shipment data into a dictionary
    shipments_dict = parse_shipment_data(shipments)

    # dictionary of items to pass to the template
    jinja_vars = {
        'shipments': shipments_dict
    }

    return render_template('shipments/shipments.html', **jinja_vars)

# shipment update endpoint
@shipments.route('/shipments_update', methods=['GET', 'POST'])
@login_required
def shipments_update_shipment():

    # check if POST was made
    if request.method == 'POST':
        
        # extract form data
        shipment_id = request.form.get("shipment-id")
        date_shipped = request.form.get("date-shipped")
        shipment_boxes = request.form.get("shipment_boxes")
        partial_delivery = request.form.get("partial_delivery")
        estimated_date = request.form.get("estimated-date")
        delivery_date = request.form.get("deliver-date")
        shipment_type = request.form.get("shipment_type")

        if all([shipment_id, date_shipped, shipment_boxes, partial_delivery, 
                estimated_date, delivery_date, shipment_type]):
            
            # fetch shipment from database
            shipment = Shipment.query.get(shipment_id)

            if not shipment:
                return redirect(url_for('shipments.shipments_home', error="Shipment not found"))
            
            # update shipment object
            shipment.date_shipped = date_shipped
            shipment.shipment_boxes = shipment_boxes
            shipment.partial_delivery = partial_delivery
            shipment.estimated_date = estimated_date
            shipment.delivery_date = delivery_date
            shipment.shipment_type = shipment_type
            
            # commit changes to database
            db.session.commit()

            # redirect back to order form
            return redirect(url_for('shipments.shipments_home'))

def create_shipment(order_id):

    print(f"Creating shipment for order ID: {order_id}")
    order = Order.query.get(order_id)
    if not order:
        raise ValueError(f"Order ID {order_id} does not exist")
    total_products = sum(item.quantity for item in order.order_items)
    shipment_boxes = (total_products + 4) // 5

    new_shipment = Shipment(
        order_id=order.id,
        date_shipped=None,
        shippment_boxes=shipment_boxes,
        partial_delivery=False,
        estimated_date=order.shipping_date,
        delivery_date=None,
        shippment_type=order.shipping_type
    )

    db.session.add(new_shipment)
    db.session.commit()
    shipments = Shipment.query.all()
    print(shipments)

    return new_shipment
