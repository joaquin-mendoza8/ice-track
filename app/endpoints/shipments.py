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
        shippment_boxes = request.form.get("shippment_boxes")
        partial_delivery = request.form.get("partial_delivery")
        estimated_date = request.form.get("estimated-date")
        delivery_date = request.form.get("deliver-date")
        shippment_type = request.form.get("shippment_type")
        
        # ensure all fields are made
        if all([shipment_id, date_shipped, shippment_boxes, partial_delivery, 
                estimated_date, delivery_date, shippment_type]):
            
            # fetch shipment from database
            shipment = Shipment.query.get(shipment_id)

            if not shipment:
                return redirect(url_for('shipments.shipments_home', error="Shipment not found"))
            
            # update shipment object
            shipment.date_shipped = date_shipped
            shipment.shippment_boxes = shippment_boxes
            shipment.partial_delivery = partial_delivery
            shipment.estimated_date = estimated_date
            shipment.delivery_date = delivery_date
            shipment.shippment_type = shippment_type
            
            # commit changes to database
            db.session.commit()

            # redirect back to order form
            return redirect(url_for('shipments.shipments_home'))

