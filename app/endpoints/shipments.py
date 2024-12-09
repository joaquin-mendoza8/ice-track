from flask import Blueprint, request, redirect, url_for, render_template, jsonify
from flask_login import login_required
from app.utils.data import *
from app.models import Product, User, Order, OrderItem, Shipment
from app.extensions import db
from datetime import datetime, timedelta
from app.utils.checks import remove_expired_shipments

# create the shipments blueprint
shipments = Blueprint('shipments', __name__)

# shipments home endpoint
@shipments.route('/shipments', methods=['GET'])
@login_required
def shipments_home():

    # check if a message was passed
    msg = request.args.get('msg')
    msg_type = request.args.get('msg_type')
    order_id = request.args.get('order_id')

    # remove all expired shipments
    remove_expired_shipments()

    # fetch all shipments from database
    shipments = Shipment.query.all()

    # parse the shipment data into a dictionary
    shipments_dict = parse_shipment_data(shipments)

    # dictionary of items to pass to the template
    jinja_vars = {
       'shipments': shipments_dict
    }

    # add order_id to dictionary from shipment_id if it exists
    if order_id:
        order = Order.query.get(order_id)
        if order:
            jinja_vars['order_id'] = order.id
        else:
            msg = "Order not found"

    # add message to dictionary if it exists
    if msg:
        jinja_vars['msg'] = msg
        jinja_vars['msg_type'] = msg_type

    return render_template('shipments/shipments.html', **jinja_vars)

# shipment update endpoint
@shipments.route('/shipments_update', methods=['POST'])
@login_required
def shipments_update_shipment():

    if request.method == 'POST':

        try:

            msg, msg_type = '', ''
        
            # extract form data
            shipment_id = request.form.get("shipment-id-update-hidden")
            date_shipped = request.form.get("date-shipped-update")
            shipment_boxes = request.form.get("shipment-boxes-update")
            partial_delivery = bool(request.form.get("partial-delivery-update"))
            estimated_delivery_date = request.form.get("estimated-delivery-date-update")
            actual_delivery_date = request.form.get("actual-delivery-date-update")
            shipment_type = request.form.get("shipment-type-update")

            if not all([shipment_id, date_shipped, shipment_boxes, partial_delivery, 
                    estimated_delivery_date, shipment_type]):
                msg = "Missing required fields"
                print(request.form)
                print(msg)
                return redirect(url_for('shipments.shipments_home', msg=msg))
                
            # fetch shipment from database
            shipment = Shipment.query.get(shipment_id)

            if not shipment:
                msg = "Shipment not found"
                print(msg)
                return redirect(url_for('shipments.shipments_home', msg=msg))
            
            # update shipment object
            shipment.shipment_boxes = shipment_boxes
            shipment.partial_delivery = partial_delivery
            shipment.shipment_type = shipment_type

            # format dates
            try:
                shipment.date_shipped = datetime.strptime(date_shipped, "%m/%d/%Y")

                if estimated_delivery_date:
                    shipment.estimated_delivery_date = datetime.strptime(estimated_delivery_date, "%m/%d/%Y")
                if actual_delivery_date:
                    shipment.actual_delivery_date = datetime.strptime(actual_delivery_date, "%Y-%m-%d")
            except ValueError as e:
                msg = "Invalid date format"
                print(msg + f": {e}")
                return redirect(url_for('shipments.shipments_home', msg=msg))

            # commit changes to database
            db.session.commit()

            msg = "Shipment updated successfully"
            msg_type = "success"

            return redirect(url_for('shipments.shipments_home', msg=msg, msg_type=msg_type))

        except Exception as e:
            msg = "Error updating shipment"
            print(msg + f": {e}")
            db.session.rollback()
            return redirect(url_for('shipments.shipments_home', msg=msg))

 
@shipments.route('/status_report', methods=['GET'])
@login_required
def status_report():

    # fetch all shipments from database
    shipments = Shipment.query.all()

    # format the shipment data into a dictionary
    shipments = parse_shipment_data(shipments)

    # Logic for preparing the status report (if needed)
    return render_template('shipments/status_report.html', shipments=shipments)


def create_shipment(order_id):
    # TODO: add user relationship to shipment (to display customer name in shipment view)

    try:

        print(f"Creating shipment for order ID: {order_id}")

        # fetch the order from the database
        order = Order.query.get(order_id)

        # raise an error if the order does not exist
        if not order: # TODO: handle this error
            print(f"Order ID {order_id} does not exist")
            return None

        # set shipment boxes to 1 for now
        shipment_boxes = 1

        # set estimated delivery date to 5 days from order.expected_shipping_date
        estimated_delivery_date = order.expected_shipping_date + timedelta(days=5)

        # create a new shipment object
        new_shipment = Shipment(
            order_id=order.id,
            user_id=order.user_id,
            date_shipped=order.expected_shipping_date,
            shipment_boxes=shipment_boxes,
            partial_delivery=False,
            estimated_delivery_date=estimated_delivery_date,
            actual_delivery_date=None,
            shipment_type=order.shipping_type
        )

        # add the shipment to the database
        db.session.add(new_shipment)
        db.session.flush()

    except Exception as e:
        print(f"Error creating shipment: {e}")
        db.session.rollback()
        return None # TODO: handle this error

    return new_shipment


# shipment info endpoint
@shipments.route('/fetch_shipment_info', methods=['GET'])
@login_required
def fetch_shipment_info():

    msg = ''

    # extract args from the request
    shipment_id = request.args.get("shipment_id")

    # convert id to int if it exists
    if shipment_id:
        shipment_id = int(shipment_id)
    else:
        msg = "Shipment not found (missing ID)"
        print(msg)
        return jsonify({'error': msg})

    # fetch the shipment from the database
    shipment = Shipment.query.get(shipment_id)

    if shipment:

        # parse the shipment data into a dictionary
        shipment_dict = parse_shipment_data([shipment])[0]

        # convert editable date to format YYYY-MM-DD
        if shipment.actual_delivery_date:
            shipment_dict['actual_delivery_date'] = shipment.actual_delivery_date.strftime('%Y-%m-%d')
            print(shipment_dict['actual_delivery_date'])

        # convert readonly dates to format YYYY-MM-DD
        shipment_dict['date_shipped'] = shipment.date_shipped.strftime('%m/%d/%Y')
        shipment_dict['estimated_delivery_date'] = shipment.estimated_delivery_date.strftime('%m/%d/%Y')

        # add the order status to the shipment dictionary
        shipment_dict['order_status'] = shipment.order.status

        # remove the order from the shipment dictionary
        shipment_dict.pop('order')

        return jsonify(shipment_dict)
    
    else:
        msg = "Shipment not found"
        print(msg)
        return jsonify({'error': msg})
