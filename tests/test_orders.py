from app.models import ProductAllocation, Order, OrderItem, AdminConfig, User, Product
import os
import pytest

def test_orders_home(client):
    """
    Test the orders home page endpoint (GET)
    """

    # send a GET request to the orders home endpoint
    response = client.get('/orders')
    assert response.status_code == 200

@pytest.mark.skip(reason="Needs to be fixed")
def test_orders_add(client, app_instance, captured_templates):
    """
    Test adding an order from the orders page (POST)
    """

    # get shipping data from the AdminConfig
    shipping_types = AdminConfig.query.filter_by(key='supported_shipping_types').first().value
    shipping_costs = AdminConfig.query.filter_by(key='supported_shipping_costs').first().value

    # set mock shipping type/cost
    assert isinstance(shipping_types, str) and isinstance(shipping_costs, str)
    shipping_type = shipping_types.split(',')[0] if shipping_types else 'test_type'
    shipping_cost = shipping_costs.split(',')[0] if shipping_costs else 9

    # get the test user's user id
    user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id
    assert user_id

    # create dummy order items data from database
    order_items = ""

    with app_instance.app_context():
        test_product = Product.query.filter_by()

    # send a POST request to the orders add endpoint
    response = client.post('/orders_add', data={
        "user-id": user_id,
        "shipping-type": shipping_type,
        "shipping-cost": shipping_cost,
        "expected-shipping-date": '09/09/2029',
        "desired-receipt-date": '09/09/2029',
        "shipping-address": '999 Test Ave',
        "billing-address": '999 Test Ave',
        "order-status": 'pending',
        "total-cost": 9.99
    }, follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/orders'
    assert b'<title>Orders</title>'

    # check if any error messages where displayed
    template, context = captured_templates[0]
    assert template.name == 'orders/orders.html'
    assert context.get('msg_type')

    # print(context.get('msg'))

    with app_instance.app_context():
        # check if the order was added to the database
        order = Order.query.filter_by(user_id=user_id).first()
        print(response.data)
        assert order

    #     # check if 1 or more order items were created
    #     order_items = OrderItem.query.filter_by(order_id=order.id).all()
    #     assert order_items

    #     order_item_ids = [item.id for item in order_items]

    #     # check if a product allocation was created for each order item
    #     # TODO: refactor into single query
    #     product_allocations = [ProductAllocation.query.filter_by(order_item_id=id).first() for id in order_item_ids]
    #     assert all(product_allocations)


