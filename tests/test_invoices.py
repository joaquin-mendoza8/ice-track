from app.models import Invoice
from app.extensions import db


def test_invoices_home(client):
    """Test the invoices home page."""

    response = client.get('/invoices')
    assert response.request.path == '/invoices'
    assert response.status_code == 200
    assert b'<title>Invoices</title>' in response.data