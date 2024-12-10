# TODO: Stress testing with pytest-benchmark pytest
import pytest
from app.models import Product

# test the inventory home endpoint
def test_inventory_home(client):

    # send a GET request to the inventory endpoint
    response = client.get('/inventory')
    assert response.status_code == 200


@pytest.mark.parametrize("flavor, container_size, price, quantity, status, dock_date, msg", [
    (None, 'small', 1.00, 10, 'planned', '2026-01-01', "Missing fields"),
    ('test', 'small', 1.00, 10, 'planned', '2026-01-01', "Added product successfully"),
    ('test', 'small', 1.00, 10, 'actual', '2020-01-01', "Added product successfully"),
    ('test', 'small', 1.00, 10, 'planned', '2026-01-01', "Product already exists"),
])
def test_inventory_add(client, app_instance, captured_templates, flavor, \
                       container_size, price, quantity, status, dock_date, msg):
    """
    Test the inventory add endpoint with different 
    parameters and check the response message.
    """

    # add a product using test client fixture
    response = client.post('/inventory_add', data={
        "product-flavor-add": flavor,
        "product-container-size-add": container_size,
        "product-price-add": price,
        "product-quantity-add": quantity,
        "product-status-add": status,
        "product-dock-date-add": dock_date,
        "user-id": 999
    }, follow_redirects=True)

    # check if the message and response is correct
    template, context = captured_templates[0]
    assert template.name == 'inventory/inventory.html'
    assert context['msg'] == msg
    assert response.status_code == 200
    
    # check if the product was added to the database
    if msg == "Added product successfully":
        with app_instance.app_context():
            product = Product.query.filter_by(flavor=flavor, status=status).first()
            assert product is not None


@pytest.mark.parametrize("flavor, container_size, price, quantity, status, dock_date, msg", [
    ('test', 'small', 1.00, 10, 'planned', '2026-01-01', "No changes detected"),
    ('test', 'small', 0, 1, 'actual', '2026-01-01', "Price and quantity must be greater than zero"),
    ('test', 'small', 1.00, 0, 'actual', '2026-01-01', "Price and quantity must be greater than zero"),
    (None, 'small', 1.00, 10, 'planned', '2026-01-01', "Missing fields"),
    ('test', 'small', 1.00, 10, 'actual', '2026-01-02', "If the dock date is in the future, the status must be set to 'planned'"),
    ('test', 'small', 1.00, 10, 'planned', '2020-01-01', "If the dock date is in the past, the status must be set to 'actual'"),
    ('test', 'small', 5.00, 10, 'planned', '2026-01-01', "A product with the same flavor and container size already exists but with a different price"),
    ('test', 'small', 1.00, 10, 'planned', '2026-01-02', "Product updated successfully"),
    ('test', 'small', 1.00, 10, 'actual', '2020-01-01', "Planned product(s) added to existing product successfully"),
])
def test_inventory_update(client, app_instance, captured_templates, flavor, container_size, price, quantity, status, dock_date, msg):
    """Test the inventory update endpoint with different parameters and check the response message."""

    # get the product id from the database
    with app_instance.app_context():
        from app.models import Product
        product_id = Product.query.filter_by(flavor='test', status='planned').first().id

    # check if the product was added
    assert product_id is not None

    # update the product using test client fixture
    response = client.post('/inventory_update', data={
        "product-id": product_id,
        "product-flavor": flavor,
        "product-container-size": container_size,
        "product-price": price,
        "product-quantity": quantity,
        "product-status": status,
        "product-dock-date": dock_date,
    }, follow_redirects=True)

    # check if the request was successful
    assert response.status_code == 200

    # check if the message is correct
    template, context = captured_templates[0]
    assert template.name == 'inventory/inventory.html'
    assert context['msg'] == msg


# test the inventory delete endpoint (POST request)
@pytest.mark.parametrize("product_id, msg", [
    (None, "Product not found"),
    (1, "Deleted product successfully"),
    (1, "Product already deleted or user not found"),
])
def test_inventory_delete(client, app_instance, captured_templates, product_id, msg):

    # get the product id from the database
    with app_instance.app_context():
        if product_id is not None:
            from app.models import Product
            product = Product.query.filter_by(flavor='test').first()
            product_id = product.id

            # check if the product was added
            assert product_id is not None

        # mark the product as deleted using 'deleted_at' field
        response = client.post('/inventory_delete', data={
            "product-id-delete": product_id,
            "user-id-delete": 999
        }, follow_redirects=True)
        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == 'inventory/inventory.html'
        assert context['msg'] == msg

        if product_id is not None:
            # reload the product
            product = Product.query.get(product_id)

            # check if the product was deleted
            assert product.deleted_at is not None

# a dummy test that deletes all "test" products from the database
# @pytest.mark.skip
def test_delete_test_products(app_instance):

    # get the product id from the database
    with app_instance.app_context():
        from app.models import Product
        from app.extensions import db
        products = Product.query.filter_by(flavor='test').all()

        # delete all test products
        for product in products:
            db.session.delete(product)

        # commit the changes
        db.session.commit()

        # check if the products were deleted
        assert len(Product.query.filter_by(flavor='test').all()) == 0

