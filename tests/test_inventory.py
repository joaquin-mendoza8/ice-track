import pytest
from dotenv import load_dotenv

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import app
from config.config import db
from app.models import Product

load_dotenv()

# create a test client
@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

# test the inventory home endpoint
def test_inventory_home(client):

    # send a GET request to the inventory endpoint
    response = client.get('/inventory')

    # check if the response is OK
    assert response.status_code == 200

# test the inventory add endpoint (POST request)
def test_inventory_add(client):
    response = client.post('/inventory_add', data={
        "product-flavor": 'test',
        "product-container-size": 'small',
        "product-price": 1.00,
        "product-quantity": 10,
        "product-status": 'planned',
        "user-id": 999
    }, follow_redirects=True)

    # check if the product was added
    assert response.status_code == 200

# test the inventory update endpoint (POST request)
def test_inventory_update(client):

    # get the product id from the database
    with app.app_context():
        product_id = Product.query.filter_by(flavor='test').first().id

    # check if the product was added
    assert product_id is not None

    # update the product using test client
    response = client.post('/inventory_update', data={
        "product-id": product_id,
        "product-flavor": 'test',
        "product-container-size": 'medium',
        "product-price": 1.10,
        "product-quantity": 1,
        "product-status":'actual'
    }, follow_redirects=True)

    # check if the product was updated
    assert response.status_code == 200

# test the inventory delete endpoint (POST request)
def test_inventory_delete(client):

    # get the product id from the database
    with app.app_context():
        product = Product.query.filter_by(flavor='test').first()
        product_id = product.id

    # check if the product was added
    assert product_id is not None

    # mark the product as deleted using 'deleted_at' field
    response = client.post('/inventory_delete', data={
        "product-id-delete": product_id,
        "user-id": 999
    }, follow_redirects=True)

    # reload the product
    with app.app_context():
        product = Product.query.get(product_id)

    # check if the product was deleted
    assert response.status_code == 200 and product.deleted_at is not None

# a dummy test that deletes all "test" products from the database
# mark as "skip" to avoid running this test
@pytest.mark.skip
def test_delete_test_products():

    # get the product id from the database
    with app.app_context():
        products = Product.query.filter_by(flavor='test').all()

        # delete all test products
        for product in products:
            db.session.delete(product)

        # commit the changes
        db.session.commit()

        # check if the products were deleted
        assert len(Product.query.filter_by(flavor='test').all()) == 0

