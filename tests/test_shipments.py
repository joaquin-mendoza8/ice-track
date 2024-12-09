from app.extensions import db


def test_shipments_home(client):
    """Test the shipments_home endpoint."""

    response = client.get('/shipments')
    assert response.status_code == 200
    assert b'<title>Shipments</title>' in response.data


def test_shipments_home_fail(client, captured_templates):
    """Test the shipments_home endpoint with a non-admin user."""

    response = client.get(f'/shipments?order_id={-1}')
    assert response.status_code == 200
    assert b'<title>Shipments</title>' in response.data
    template, context = captured_templates[0]
    assert context.get('msg') == "Order not found"


def test_status_report(client):
    """Test the status_report endpoint."""

    response = client.get('/status_report')
    assert response.status_code == 200
    assert b'<title>Status Report</title>' in response.data