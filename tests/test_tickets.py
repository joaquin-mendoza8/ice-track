# import date object
from datetime import date
from app.extensions import db

# test the inventory home endpoint
def test_tickets_home(client):
    # send a GET request to the inventory endpoint
    response = client.get('/tickets')
    assert response.status_code == 200
    
def test_tickets_add(client, app_instance):
    response = client.post('/tickets_add', data={
        "source": 'test',
        "problem-type": 'shipping update',
        "problem-description": 'need to update shipping address'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # check if the ticket was added to the database
    with app_instance.app_context():
        from app.models import Ticket
        ticket = Ticket.query.filter_by(source='test').first()
        assert ticket is not None and ticket.date_reported is not None


def test_tickets_update_in_progress(client, app_instance):
    # get the ticket id from the database
    with app_instance.app_context():
        from app.models import Ticket
        ticket = Ticket.query.filter_by(source='test').first()
        ticket_id = ticket.id

    # check if the ticket was added
    assert ticket_id is not None
    
    response = client.post('/tickets_update', data={
        "ticket-id": ticket_id,
        "date-detected": date(2024, 1, 1), # January 1, 2024
        "problem-status": 'in-progress',
        "problem-resolution": 'we are working on a solution',
        "date-resolved": None
    }, follow_redirects=True)
    
    # reload the ticket
    ticket = Ticket.query.get(ticket_id)
        
    # ensure date detected is filled
    assert response.status_code == 200 
    assert ticket.date_detected == date(2024, 1, 1)

def test_tickets_update_resolved(client, app_instance):
     # get the product id from the database
    with app_instance.app_context():
        from app.models import Ticket
        ticket_id = Ticket.query.filter_by(source='test').first().id

    # check if the product was added
    assert ticket_id is not None
    
    # import date object
    from datetime import date
    
    response = client.post('/tickets_update', data={
        "ticket-id": ticket_id,
        "date-detected": date(2024, 1, 1), # January 1, 2024
        "problem-status": 'resolved',
        "problem-resolution": 'Changed shipping date',
        "date-resolved": date(2024, 12, 31) # December 31, 2024
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # check if the ticket was added to the database
    with app_instance.app_context():
        from app.models import Ticket
        ticket = Ticket.query.filter_by(source='test').first()
        assert ticket.date_resolved == date(2024, 12, 31)
        assert ticket.problem_status == 'resolved'
        assert ticket.problem_resolution == 'Changed shipping date'
        
def test_tickets_query(client, app_instance):
    with app_instance.app_context():
        from app.models import Ticket
        test_tickets = Ticket.query.filter_by(source='test').all()
        
        # check if the product was added
        assert test_tickets is not None
        
    response = client.get('/tickets_query', data={
        "customer-name": 'test',
    }, follow_redirects=True)
    
    assert response.status_code == 200
        
def test_tickets_delete(client, app_instance):
     # get the product id from the database
    with app_instance.app_context():
        from app.models import Ticket
        ticket = Ticket.query.filter_by(source='test').first()
        ticket_id = ticket.id

        # check if the ticket exists
        assert ticket is not None and ticket_id is not None
        
        response = client.post('/tickets_delete', data={
            "ticket-id": ticket_id,
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # reload the ticket
        ticket = Ticket.query.get(ticket_id)
        
    # check if the ticket was deleted
    assert response.status_code == 200 and ticket is None


