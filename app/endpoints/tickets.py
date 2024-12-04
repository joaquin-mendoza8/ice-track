from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required, current_user
from app.utils.data import *
from app.models import Product, User, Ticket
from app.extensions import db
from datetime import datetime, date, timezone, timedelta

# create the trouble tickets blueprint
tickets = Blueprint('tickets', __name__)

# tickets home endpoint
@tickets.route('/tickets', methods=['GET'])
@login_required
def tickets_home():
    # fetch all tickets and customers that are not admin from the database
    if current_user.is_admin:
        tickets = Ticket.query.all()
    else:
        user_source = current_user.first_name + " " + current_user.last_name
        tickets = Ticket.query.filter_by(source=user_source).all()
        
    customers = User.query.filter_by(is_admin=False).all()
    start_date = min((ticket.date_reported for ticket in tickets), default=date(2024, 1, 1))
    end_date = date.today()
    
    tickets_dict = parse_ticket_data(tickets)
    customers_dict = parse_customer_data(customers)
    statistics_dict = create_ticket_statistics(tickets, start_date, end_date)
    
    jinja_vars = {'tickets' : tickets_dict,
                  'customers' : customers_dict,
                  'statistics': statistics_dict}
    
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

@tickets.route('/tickets_delete', methods=['POST'])
def tickets_delete_ticket():
    if request.method == 'POST': 
       
        ticket_id = request.form.get('ticket-id')
        ticket = Ticket.query.get(ticket_id)
        db.session.delete(ticket)
        db.session.commit()
        
        return redirect(url_for('tickets.tickets_home'))
    
    return render_template('tickets/tickets.html')

@tickets.route('/tickets_query', methods=['GET'])
def tickets_query_tickets():
    if request.method == 'GET':
        # Extract form data from query form
        customer_name = request.args.get('customer-name') # customer name == source
        problem_type = request.args.get('problem-type')
        problem_status = request.args.get('problem-status')
        date_reported_start = request.args.get('date-reported-start')
        date_reported_end = request.args.get('date-reported-end')
        date_resolved_start = request.args.get('date-resolved-start')
        date_resolved_end = request.args.get('date-resolved-end')
        
        # Base query
        query = Ticket.query
        
        # Apply filters dynamically
        if customer_name:
            query = query.filter(Ticket.source.ilike(f"%{customer_name}%"))
            
        if problem_type:
            query = query.filter(Ticket.problem_type.ilike(f"%{problem_type}%"))
            
        if problem_status:
            query = query.filter(Ticket.problem_status.ilike(problem_status))
            
        if date_reported_start:
            query = query.filter(Ticket.date_reported >= datetime.strptime(date_reported_start, '%Y-%m-%d').date())
            
        if date_reported_end:
            query = query.filter(Ticket.date_reported <= datetime.strptime(date_reported_end, '%Y-%m-%d').date())
            
        if date_resolved_start:
            query = query.filter(Ticket.date_resolved >= datetime.strptime(date_resolved_start, '%Y-%m-%d').date())
        
        if date_resolved_end:
            query = query.filter(Ticket.date_resolved <= datetime.strptime(date_resolved_end, '%Y-%m-%d').date())

        # Fetch the filtered results
        filtered_tickets = query.all()

        # Convert tickets to dictionary format for rendering
        queried_tickets_dict = parse_ticket_data(filtered_tickets)
        
        # calculate start and end dates
        start_date = date(1970, 1, 1) if not date_reported_start else datetime.strptime(date_reported_start, '%Y-%m-%d').date()
        end_date = date.today() if not date_reported_end else datetime.strptime(date_reported_end, '%Y-%m-%d').date()
    
        # requery and parse customers for add ticket model
        customers = User.query.filter_by(is_admin=False).all()
        customers_dict = parse_customer_data(customers)
        statistics_dict = create_ticket_statistics(filtered_tickets, start_date, end_date)
        
        jinja_vars = {'tickets' : queried_tickets_dict,
                        'customers' : customers_dict,
                        'statistics' : statistics_dict}

        # Pass filtered results to the template
        return render_template('tickets/tickets.html', **jinja_vars)
    
    # On GET request, simply render the ticket query page
    return render_template('tickets/tickets.html')

@tickets.route('/tickets_summary', methods=['GET'])
def tickets_summary():
    return None

def create_ticket_statistics(tickets, start_date: date = None, end_date: date = None) -> dict:
    statistics = {
        'average_time_to_close': 'N/A',
        'average_opened_problems_per_day': 'N/A',
        'average_problems_worked_per_day': 'N/A'
    }
    
    # case if there are no tickets
    if not tickets:
        return statistics
    
    # filters tickets based on start date and end date
    if start_date:
        tickets = [ticket for ticket in tickets if ticket.date_reported >= start_date]

    if end_date:
        tickets = [ticket for ticket in tickets if ticket.date_resolved is None or ticket.date_resolved <= end_date]
    
    # calculate average time it takes to resolve tickets
    closed_tickets = [ticket for ticket in tickets if ticket.date_resolved]
    if closed_tickets:
        total_close_time = sum((t.date_resolved - t.date_reported).total_seconds() for t in closed_tickets)
        statistics['average_time_to_close'] = round(total_close_time / len(closed_tickets) / 86400, 2)  # Convert seconds to days and rounds to 2 decimal places
    
    # all date ranges for averaging daily counts
    all_dates = [ticket.date_reported for ticket in tickets] + [ticket.date_resolved for ticket in closed_tickets if ticket.date_resolved]
    min_date = start_date or (min(all_dates) if all_dates else datetime.now())
    max_date = end_date or (max(all_dates) if all_dates else datetime.now())
    
    # calculate average Number of open tickets per day
    current_date = min_date
    open_ticket_counts_per_day = []
    while current_date <= max_date:
        open_tickets = [
            ticket for ticket in tickets 
            if (ticket.date_resolved is None or ticket.date_resolved <= current_date)
        ]
        open_ticket_counts_per_day.append(len(open_tickets))
        current_date += timedelta(days=1)

    if open_ticket_counts_per_day:
        statistics['average_open_problems_per_day'] = round(sum(open_ticket_counts_per_day) / len(open_ticket_counts_per_day), 2)
        
    # Average Number of Problems Being Worked On/Day
    current_date = min_date
    in_progress_tickets_per_day = []
    while current_date <= max_date:
        in_progress_tickets = [
            ticket for ticket in tickets 
            if ticket.date_detected is not None
            and ticket.date_detected <= current_date
            and ticket.problem_status == 'in-progress'
        ]
        print(tickets)
        print(in_progress_tickets, current_date, max_date)
        in_progress_tickets_per_day.append(len(in_progress_tickets))
        current_date += timedelta(days=1)

    if in_progress_tickets_per_day:
        statistics['average_problems_worked_per_day'] = round(sum(in_progress_tickets_per_day) / len(in_progress_tickets_per_day), 2)
    
    return statistics