from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required
from app.utils.data import *
from app.models import Product, User, Ticket
from app.extensions import db
from datetime import datetime, timezone

# create the trouble tickets blueprint
tickets = Blueprint('tickets', __name__)

# tickets home endpoint
@tickets.route('/tickets', methods=['GET'])
@login_required
def tickets_home():
    
    # fetch all tickets and customers that are not admin from the database
    tickets = Ticket.query.all()
    customers = User.query.filter_by(is_admin=False).all()
    
    tickets_dict = parse_ticket_data(tickets)
    customers_dict = parse_customer_data(customers)
    
    jinja_vars = {'tickets' : tickets_dict,
                  'customers' : customers_dict}
    
    return render_template('tickets/tickets.html', **jinja_vars)

@tickets.route('/tickets_add', methods=['GET', 'POST'])
def tickets_add_ticket():
     # check if POST request was made
    if request.method == 'POST':

        # extract form data
        source = request.form.get('source')
        problem_type = request.form.get('problem-type')
        problem_description = request.form.get('problem-description')
        
        # ensure all fields are filled
        if all([ source, problem_type, problem_description ]):
                    
                # initialize the ticket object
                new_ticket = Ticket(
                    source=source,
                    problem_type=problem_type,
                    problem_description=problem_description
                )
    
                # add the order to the database
                db.session.add(new_ticket)
                db.session.commit()
    
                # redirect back to the ticket form
                return redirect(url_for('tickets.tickets_home'))

    return render_template('tickets/tickets.html')

@tickets.route('/tickets_update', methods=['GET', 'POST'])
def tickets_update_ticket():
    if request.method == 'POST':

        # extract form data
        id = request.form.get('ticket-id')
        date_detected = request.form.get('date-detected')
        problem_status = request.form.get('problem-status')
        problem_resolution = request.form.get('problem-resolution')
        date_resolved = request.form.get('date-resolved')
        
        # ensure that date_detected has a default value of current date if no input was given
        if date_detected == None: 
            date_detected = datetime.now(timezone.utc).date()
            
        # the only required form field is problem_status
        if problem_status:
            
            # retrieve the current ticket from the db using the id
            ticket = Ticket.query.get(id)
            
            # update the current ticket in the db with the new form fields
            if date_detected:
                ticket.date_detected = datetime.strptime(date_detected, '%Y-%m-%d').date() # convert string to datetime object
                
            if date_resolved:
                ticket.date_resolved = datetime.strptime(date_resolved, '%Y-%m-%d').date()
                
            ticket.problem_status = problem_status
            ticket.problem_resolution = problem_resolution
            
            # persist the updated ticket to the database
            db.session.commit()
            
            # redirect back to the ticket form
            return redirect(url_for('tickets.tickets_home'))
            
    return render_template('tickets/tickets.html')

@tickets.route('/tickets_delete', methods=['DELETE'])
def tickets_tickets_delete():
    if request.method == 'DELETE':
        
        
        
        # redirect back to the ticket form
        return redirect(url_for('tickets.tickets_home'))
    
    return render_template('tickets/tickets.html')