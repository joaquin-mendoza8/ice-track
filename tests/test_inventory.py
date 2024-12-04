# TODO: Stress testing with pytest-benchmark pytest

# test the inventory home endpoint
def test_inventory_home(client):

    # send a GET request to the inventory endpoint
    response = client.get('/inventory')
    assert response.status_code == 200

# test the inventory add endpoint (POST request)
def test_inventory_add(client, app_instance, captured_templates):
    response = client.post('/inventory_add', data={
        "product-flavor-add": 'test',
        "product-container-size-add": 'small',
        "product-price-add": 1.00,
        "product-quantity-add": 10,
        "product-status-add": 'planned',
        "product-dock-date-add": '2026-01-01',
        "user-id": 999
    }, follow_redirects=True)
    template, context = captured_templates[0]
    assert template.name == 'inventory/inventory.html'
    assert context['msg'] == "Added product successfully"
    assert response.status_code == 200
    
    # check if the product was added to the database
    with app_instance.app_context():
        from app.models import Product
        product = Product.query.filter_by(flavor='test').first()
        assert product is not None

# test the inventory update endpoint (POST request)
def test_inventory_update(client, app_instance):

    # get the product id from the database
    with app_instance.app_context():
        from app.models import Product
        product_id = Product.query.filter_by(flavor='test').first().id

    # check if the product was added
    assert product_id is not None

    # update the product using test client
    response = client.post('/inventory_update', data={
        "product-id": product_id,
        "product-flavor": 'test',
        "product-container-size": 'small',
        "product-price": 1.10,
        "product-quantity": 1,
        "product-status": 'planned',
        "product-dock-date": '2026-01-01',
    }, follow_redirects=True)

    # check if the product was updated
    assert response.status_code == 200

# test the inventory delete endpoint (POST request)
def test_inventory_delete(client, app_instance):

    # get the product id from the database
    with app_instance.app_context():
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

        # reload the product
        product = Product.query.get(product_id)

    # check if the product was deleted
    assert response.status_code == 200 and product.deleted_at is not None

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

