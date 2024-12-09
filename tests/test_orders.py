from app.models import ProductAllocation, Order, OrderItem, AdminConfig, \
    User, Product, Shipment, Invoice
from app.extensions import db
import os
import pytest
from datetime import datetime


def get_shipping_data():
    shipping_types = AdminConfig.query.filter_by(key='supported_shipping_types_test').first().value
    shipping_costs = AdminConfig.query.filter_by(key='supported_shipping_costs_test').first().value
    return shipping_types.split(',')[0], shipping_costs.split(',')[0]


def create_order_add_data(user_id, product, shipping_type, shipping_cost):
    # create dummy order data from test product
    order_items = {
        "order_items[0][flavor]": product.flavor,
        "order_items[0][container-size]": product.container_size,
        "order_items[0][quantity]": 1,
        "order_items[0][line-item-cost]": product.price,
    }
    data = {
        "user-id": user_id,
        "customer-status": 'preferred',
        "shipping-type": shipping_type,
        "shipping-cost": shipping_cost,
        "expected-shipping-date": '09/09/2029',
        "desired-receipt-date": '2029-09-09',
        "shipping-address": '999 Test Ave',
        "billing-address": '999 Test Ave',
        "order-status": 'pending',
        "total-cost": float(product.price) + float(shipping_cost),
    }
    data.update(order_items)
    return data


def create_order_update_data(user_id, order_id, product, shipping_type, shipping_cost):
    # create dummy order data from test product
    order_items = {
        "order_items[0][flavor]": product.flavor,
        "order_items[0][container-size]": product.container_size,
        "order_items[0][quantity]": 2,
        "order_items[0][line-item-cost]": product.price,
    }
    data = {
        "order-user-id-update-hidden": user_id,
        "order-id-update-hidden": order_id,
        "shipping-type-update": shipping_type,
        "shipping-cost-update": shipping_cost,
        "desired-receipt-date-update": '09/09/2029',
        "billing-address-update": '999 New Test Ave',
        "order-status-update": 'pending',
        "order-total-cost-hidden": float(product.price) + float(shipping_cost),
    }
    data.update(order_items)
    return data


def test_orders_add(client, app_instance, captured_templates, test_product, test_admin_config):
    with app_instance.app_context():
        # get the test user's user id
        user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id
        assert user_id

        # get the test shipping data
        shipping_type, shipping_cost = get_shipping_data()
        assert shipping_type and shipping_cost

        # create order data
        data = create_order_add_data(user_id, test_product, shipping_type, shipping_cost)

        # send a POST request to the orders add endpoint
        response = client.post('/orders_add', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/orders'
        assert b'<title>Orders</title>'

        # check if any error messages where displayed
        template, context = captured_templates[0]
        assert template.name == 'orders/orders.html'
        assert context.get('msg_type')

        # check if the order was added to the database
        order = Order.query.filter_by(user_id=user_id).first()
        assert order
        assert order.shipping_type == shipping_type
        assert order.shipping_cost == float(shipping_cost)

        # check if 1 or more order items were created
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        assert order_items and len(order_items) == 1

        # check if a product allocation was created for each order item
        product_allocations = [ProductAllocation.query.filter_by(order_item_id=item.id).first() for item in order_items]
        assert all(product_allocations)
        assert all([allocation.product_id == test_product.id for allocation in product_allocations])
        assert all([allocation.quantity_allocated == 1 for allocation in product_allocations])
        assert all([allocation.disposition == 'committed' for allocation in product_allocations])

        # check if a shipment was created for the order
        shipment = Shipment.query.filter_by(order_id=order.id).first()
        assert shipment
        assert shipment.shipment_boxes == 1

        # check if an invoice was created for the order
        invoice = Invoice.query.filter_by(order_id=order.id).first()
        assert invoice
        assert invoice.total_cost == order.total_cost

        # check if the product quantity was updated
        product = Product.query.filter_by(flavor=test_product.flavor).first()
        assert product.quantity == test_product.quantity - 1
        assert product.committed_quantity == 1


@pytest.mark.parametrize("iter", [
    1,
    2,
    3,
    4,
])
def test_orders_update(client, app_instance, captured_templates, test_product, test_admin_config, iter):
    """Test updating an order from the orders page (POST)"""

    with app_instance.app_context():
        # get the test user's user id
        user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id
        assert user_id

        # get the test order id from the database
        order_id = Order.query.filter_by(user_id=user_id).first().id
        assert order_id

        # get the test shipping data
        shipping_type, shipping_cost = get_shipping_data()
        assert shipping_type and shipping_cost

        # create order data with new billing address
        data = create_order_update_data(user_id, order_id, test_product, shipping_type, shipping_cost)

        # if the iteration is 3, add a new order item
        if iter == 3:
            data.update({
                "order_items[1][flavor]": test_product.flavor,
                "order_items[1][container-size]": test_product.container_size,
                "order_items[1][quantity]": 1,
                "order_items[1][line-item-cost]": test_product.price,
            })

        # send a POST request to the orders update endpoint
        response = client.post('/orders_update', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/orders'
        assert b'<title>Orders</title>'

        # check if any error messages where displayed
        template, context = captured_templates[0]
        assert template.name == 'orders/orders.html'

        # check if the correct message was displayed based on the iteration
        if iter == 1:
            assert context.get('msg_type') and context['msg_type'] == 'success'
            assert context.get('msg') == "Order item updated"
        elif iter == 2 or iter == 3:
            assert context.get('msg_type') and context['msg_type'] == 'info'
            assert context.get('msg') == "No changes made"
        elif iter == 4:
            assert context.get('msg_type') and context['msg_type'] == 'success'
            assert context.get('msg') == "Order updated successfully"

        # check if the order was updated in the database
        order = Order.query.filter_by(id=order_id).first()
        assert order
        assert order.billing_address == data['billing-address-update']

        # check if the order item was updated
        order_item = OrderItem.query.filter_by(order_id=order_id).first()
        assert order_item.quantity == 2

        # check if the invoice was updated
        invoice = Invoice.query.filter_by(order_id=order_id).first()
        assert invoice.total_cost == order.total_cost

        # check if the product allocation was updated
        product_allocation = ProductAllocation.query.filter_by(order_id=order_id).first()
        assert product_allocation.quantity_allocated == 2

        # check if the product quantity was updated
        product = Product.query.filter_by(flavor=test_product.flavor).first()
        if iter == 3:
            assert product.quantity == test_product.quantity - 3
            assert product.committed_quantity == 3
        else:
            assert product.quantity == test_product.quantity - 2
            assert product.committed_quantity == 2


def test_orders_fetch_sizes(client, test_product):
    """Test fetching container sizes for a product (GET)"""

    # send a GET request to the orders fetch sizes endpoint
    response = client.get(f'/orders/fetch_sizes?flavor={test_product.flavor}', follow_redirects=True)
    assert response.status_code == 200

    # check if the json response equals the test product's container size
    assert response.json == {'sizes': [test_product.container_size]}


def test_orders_fetch_stock(client, test_product):
    """Test fetching stock for a product (GET)"""

    # send a GET request to the orders fetch stock endpoint
    response = client.get(f'/orders/fetch_stock?flavor={test_product.flavor}&container-size={test_product.container_size}', 
                          follow_redirects=True)
    assert response.status_code == 200

    # check if the json response equals the test product's quantity
    product_quantity = Product.query.filter_by(flavor=test_product.flavor, container_size=test_product.container_size).first().quantity
    assert response.json == {
        'stock': product_quantity,
        'status': test_product.status,
        'dock_date': test_product.dock_date.strftime('%m/%d/%Y')
    }


def test_orders_fetch_cost(client, test_product):
    """Test fetching the cost for a product (GET)"""

    # send a GET request to the orders fetch cost endpoint
    response = client.get(
        f'/orders/fetch_cost?flavor={test_product.flavor}&container-size={test_product.container_size}&quantity=1', 
                          follow_redirects=True)
    assert response.status_code == 200

    # check if the json response equals the test product's price
    assert response.json == {'cost': test_product.price}


def test_orders_fetch_product_status(client, test_product):
    """Test fetching the status for a product (GET)"""

    # send a GET request to the orders fetch product status endpoint
    response = client.get(
        f'/orders/fetch_product_status?flavor={test_product.flavor}&container-size={test_product.container_size}', 
        follow_redirects=True)
    assert response.status_code == 200

    # check if the json response equals the test product's status
    assert response.json == {'status': test_product.status}


def test_orders_fetch_order_info(client, test_product):
    """Test fetching order info for a product (GET)"""

    # get the test user's user id
    user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id
    assert user_id

    # get the test order id from the database
    order = Order.query.filter_by(user_id=user_id).first()
    order_id = order.id
    assert order_id

    # send a GET request to the orders fetch order info endpoint
    response = client.get(f'/orders/fetch_order_info?order_id={order_id}', follow_redirects=True)
    assert response.status_code == 200

    # check if the json response equals the test product's status
    assert "error" not in response.json


def test_current_invoice(client, captured_templates):
    """Test the current invoice endpoint (GET)"""

    # get the test user's user id
    user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id
    assert user_id

    # get the invoice id from the database
    invoice = Invoice.query.filter_by(user_id=user_id).first()
    print(invoice)
    assert invoice
    invoice_id = invoice.id

    # send a GET request to the current invoice endpoint
    response = client.get(f'/current-invoice/{invoice_id}', follow_redirects=True)
    assert response.status_code == 200

    # check if the current invoice page was rendered
    template, context = captured_templates[0]
    assert template.name == 'invoices/current_invoice.html'
    assert not context.get('msg')


@pytest.mark.parametrize("iter, msg", [
    (1, 'Missing required fields'),
    (2, 'Shipment not found'),
    (3, "Invalid date format"),
    (4, "Shipment updated successfully")
])
def test_update_shipment(client, app_instance, captured_templates, iter, msg):
    """Test updating a shipment from the orders page (POST)"""

    with app_instance.app_context():
        # get the test user's user id
        user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id
        assert user_id

        # get the test order id from the database
        order_id = Order.query.filter_by(user_id=user_id).first().id
        assert order_id

        # get the test shipment id from the database
        shipment = Shipment.query.filter_by(order_id=order_id).first()
        assert shipment
        shipment_id = shipment.id

        # prepare the shipment data
        data = {
            "shipment-id-update-hidden": shipment_id,
            "date-shipped-update": shipment.date_shipped.strftime('%m/%d/%Y'),
            "shipment-boxes-update": shipment.shipment_boxes,
            "estimated-delivery-date-update": shipment.estimated_delivery_date.strftime('%m/%d/%Y'),
            "actual-delivery-date-update": datetime.now().strftime('%Y-%m-%d'),
            "shipment-type-update": shipment.shipment_type
        }

        # add fields that will cause errors in the update
        if iter != 1:
            data["partial-delivery-update"] = shipment.partial_delivery

        if iter == 2:
            data["shipment-id-update-hidden"] = -1
        elif iter == 3:
            data['date-shipped-update'] = 'invalid date'
            
        # send a POST request to the update shipment endpoint
        response = client.post('/shipments_update', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/shipments'
        assert b'<title>Shipments</title>'

        # check if any error messages where displayed
        template, context = captured_templates[0]
        assert template.name == 'shipments/shipments.html'

        if iter != 4:
            assert context.get('msg') == msg
        else:
            assert context.get('msg_type') and context['msg_type'] == 'success'
            assert context.get('msg') == "Shipment updated successfully"


@pytest.mark.parametrize("iter, msg", [
    (1, "Missing fields"),
    (2, "Allocation not found"),
    (3, "Allocation updated successfully")
])
def test_update_allocation(client, app_instance, iter, msg):
    """Test updating a product allocation from the orders page (GET)"""

    # get the test user's user id
    user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id
    assert user_id

    # get the test order id from the database
    order_id = Order.query.filter_by(user_id=user_id).first().id
    assert order_id

    # get the test product allocation id from the database
    product_allocation = ProductAllocation.query.filter_by(order_id=order_id).first()
    assert product_allocation
    allocation_id = product_allocation.id
    disposition = product_allocation.disposition

    # alter the data based on the iteration to cause errors
    if iter == 1:
        disposition = ''
    if iter == 2:
        allocation_id = -1
    
    # send a GET request to the update allocation endpoint
    response = client.get(f'/inventory_update_allocation?id={allocation_id}&disposition={disposition}', follow_redirects=True)

    # check if the response was successful and the correct message was displayed
    assert response.status_code == 200
    assert response.json == {
        'msg': msg,
        'msg_type': 'success' if iter == 3 else 'error'
    }


def test_fetch_shipment_info(client, app_instance, captured_templates):
    """Test fetching shipment info for an order (GET)"""

    with app_instance.app_context():
        # get the test user's user id
        user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id
        assert user_id

        # get the test shipment id from the database
        shipment = Shipment.query.filter_by(user_id=user_id).first()
        assert shipment
        shipment_id = shipment.id

        # send a GET request to the fetch shipment info endpoint
        response = client.get(f'/fetch_shipment_info?shipment_id={shipment_id}', follow_redirects=True)
        assert response.status_code == 200

        # check if the json response contains the shipment info
        assert "error" not in response.json


def test_orders_cancel(client, app_instance, captured_templates, test_product):

    """Test cancelling an order from the orders page (POST)"""

    # get the test user's user id
    user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id
    
    # get the test order id from the database
    order_id = Order.query.filter_by(user_id=user_id).first().id
    assert order_id

    # send a POST request to the orders cancel endpoint
    response = client.post('/orders_cancel', data={"order-id-cancel": order_id}, follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/orders'
    assert b'<title>Orders</title>'

    # check if any error messages where displayed
    template, context = captured_templates[0]
    assert template.name == 'orders/orders.html'
    assert context.get('msg_type')

    # check if the order was cancelled from the database
    order = Order.query.filter_by(id=order_id).first()
    assert order and order.status == 'cancelled'

    # check if the product allocations were removed
    product_allocations = ProductAllocation.query.filter_by(order_id=order_id).all()
    assert product_allocations == []

    # check if the product quantities were updated
    product = Product.query.filter_by(flavor='test').first()
    assert product.quantity == 10
    assert product.committed_quantity == 0


def test_orders_delete(client, app_instance, captured_templates, test_product):
    """Test deleting an order from the orders page (POST)"""

    with app_instance.app_context():
        # get the test user's user id
        user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id
        assert user_id

        # get the test user's order
        order = Order.query.filter_by(user_id=user_id).first()
        assert order is not None

        # send a POST request to the orders delete endpoint
        response = client.post('/orders_delete', data={"order-id-delete": order.id}, follow_redirects=True)

        assert response.status_code == 200
        assert response.request.path == '/orders'
        assert b'<title>Orders</title>'

        # check if any error messages where displayed
        template, context = captured_templates[0]
        assert template.name == 'orders/orders.html'
        assert context.get('msg_type') and context['msg_type'] == 'success'

        # check if the order was removed from the database
        order = Order.query.filter_by(user_id=user_id).first()
        assert order is None

        # check if the product quantities were updated
        product = Product.query.filter_by(flavor='test').first()
        assert product.quantity == 10
        assert product.committed_quantity == 0

        # check if the shipment was removed
        shipment = Shipment.query.filter_by(user_id=user_id).first()
        assert shipment is None

        # check if the invoice was removed
        invoice = Invoice.query.filter_by(user_id=user_id).first()
        assert invoice is None


def test_orders_home(client):
    """Test the orders home page endpoint (GET)."""

    # send a GET request to the orders home endpoint
    response = client.get('/orders')
    assert response.status_code == 200


# @pytest.mark.skip(reason="Needs to be fixed")
def test_delete_order_dependencies(app_instance):
    """
    Test deleting an order's dependencies (order_items, product_allocations, shipment, invoice, order)
    """

    with app_instance.app_context():
        # get the test user's user id
        user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id
        assert user_id

        # get the test user's order
        orders = Order.query.filter_by(user_id=user_id).all()
        if orders:
            for order in orders:
                # delete all order items with the order id = order.id
                OrderItem.query.filter_by(order_id=order.id).delete()

                # delete all product allocations with the order item id in order.order_items
                ProductAllocation.query.filter_by(order_id=order.id).delete()
                Shipment.query.filter_by(order_id=order.id).delete()
                Invoice.query.filter_by(order_id=order.id).delete()
                Order.query.filter_by(user_id=user_id).delete()
                db.session.commit()

                # check if the order and its dependencies were deleted
                assert OrderItem.query.filter_by(order_id=order.id).all() == []
                assert ProductAllocation.query.filter_by(order_id=order.id).all() == []
                assert Shipment.query.filter_by(order_id=order.id).all() == []
                assert Invoice.query.filter_by(order_id=order.id).all() == []
                assert Order.query.filter_by(user_id=user_id).first() is None