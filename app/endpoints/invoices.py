from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import current_user, login_required
from app.utils.data import parse_invoice_data
from app.models import Invoice
from app.extensions import db

# create the home blueprint
invoices = Blueprint('invoices', __name__)

# TODO: create invoices

invoices_data = [
    {
        "id": 12345,
        "customer_name": "John Doe",
        "order_items": [
            {"name": "Vanilla Ice Cream", "quantity": 2, "unit_price": 10, "total": 20},
            {"name": "Chocolate Ice Cream", "quantity": 1, "unit_price": 12, "total": 12},
        ],
        "total": 32,
        "due_date": "2024-11-10",
    },
    {
        "id": 67890,
        "customer_name": "Jane Smith",
        "order_items": [
            {"name": "Strawberry Ice Cream", "quantity": 3, "unit_price": 15, "total": 45},
        ],
        "total": 45,
        "due_date": "2024-11-15",
    },
]

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