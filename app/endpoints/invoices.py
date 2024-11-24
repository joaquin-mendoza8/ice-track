from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import current_user, login_required

# create the home blueprint
invoices = Blueprint('invoices', __name__)

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

    # if user is not logged in, redirect to login
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template("invoices/invoices.html", invoices=invoices_data)

@invoices.route('/current-invoice/<int:invoice_id>')
@login_required
def current_invoice(invoice_id):
    invoice = next((o for o in invoices_data if o['id'] == invoice_id), None)
    if not invoice:
        return "Invoice not found", 404
    
    print(invoice)
    return render_template('invoices/current_invoice.html', invoice=invoice)