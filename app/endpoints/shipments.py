from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required
from app.utils.data import *
from app.models import Product, User, Order, OrderItem, Shipment
from app.extensions import db

# create the shipments blueprint
shipments = Blueprint('shipments', __name__)

# shipments home endpoint
@shipments.route('/shipments', methods=['GET'])
@login_required
def shipments_home():

    # fetch all shipments from database
    shipments = Shipment.query.all()

    # fetch all orders from database
    #orders = Order.query.all()

    #parse the shipment data into a dictionary
    shipments_dict = parse_product_data(shipments)
    #orders_dict = parse_order_data(orders)

    # dictionary of items to pass to the template
    jinja_vars = {
        #'orders': orders_dict,
        'shipments': shipments_dict
    }

    return render_template('shipments/shipments.html', **jinja_vars)

# shipment update endpoint
@shipments.route('/shipments_update', methods=['GET', 'POST'])
@login_required
def shipments_update_shipment():

    if request.method == 'POST':

        #order_id = request.form.get("order-id")
        shipment_id = request.form.get("shipment-id")

        date_shipped = request.form.get("date-shipped")
        shipment_boxes = request.form.get("shipment_boxes")
        partial_delivery = request.form.get("partial_delivery")
        estimated_date = request.form.get("estimated-date")
        delivery_date = request.form.get("deliver-date")
        shipment_type = request.form.get("shipment_type")

        if all([shipment_id, date_shipped, shipment_boxes, partial_delivery, 
                estimated_date, delivery_date, shipment_type]):
            
            shipment = Shipment.query.get()

            shipment.date_shipped = date_shipped
            shipment.shipment_boxes = shipment_boxes
            shipment.partial_delivery = partial_delivery
            shipment.estimated_date = estimated_date
            shipment.delivery_date = delivery_date
            shipment.shipment_type = shipment_type
            
            db.session.commit()

            return redirect(url_for('shipments.shipments_home'))

