from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import current_user, login_required
from app.utils.data import parse_invoice_data
from app.models import Invoice
from app.extensions import db

# create the home blueprint
invoices = Blueprint('invoices', __name__)

# create the home endpoint
@invoices.route('/invoices')
@login_required
def invoices_home():

    try:

        msg = ''

        # fetch all invoices from database
        invoices = Invoice.query.all()

        # update days overdue for each invoice
        for invoice in invoices:
            days_overdue = invoice.compute_days_overdue()
            if days_overdue != invoice.days_overdue:
                invoice.days_overdue = days_overdue
        
        # commit if changes were made
        if db.session.dirty:
            db.session.commit()

        # format the invoices data into a dictionary
        invoices_dict = parse_invoice_data(invoices)

        jinja_vars = {
            "invoices": invoices_dict,
        }

        return render_template("invoices/invoices.html", **jinja_vars, msg=msg)


    except Exception as e:
        print(e)
        msg = e
        return render_template("invoices/invoices.html", msg=msg)


@invoices.route('/current-invoice/<int:invoice_id>')
@login_required
def current_invoice(invoice_id):

    # get the invoice from the database
    invoice = Invoice.query.get(invoice_id)

    # calculate the subtotal (line items total)
    subtotal = sum([item.line_item_cost for item in invoice.order.order_items])

    jinja_vars = {
        "invoice": invoice,
        "subtotal": subtotal,
    }

    if not invoice:
        return "Invoice not found", 404

    return render_template('invoices/current_invoice.html', **jinja_vars)