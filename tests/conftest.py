import pytest
import os
import sys
from werkzeug.security import generate_password_hash
from flask import template_rendered

# add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import create_app
from config.config import TestConfig
from app.models import User, Product, ProductAllocation, AdminConfig
from app.extensions import db
from datetime import datetime

# load environment variables (local only)
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()
else:
    print("No .env file found, using CI environment variables.")

# 1. Create and configure the test app
@pytest.fixture(scope="session")
def app_instance():
    app = create_app(TestConfig)
    with app.app_context():
        yield app

# 2. Seed the database with a test user, if not already present
@pytest.fixture(scope="session")
def seed_database(app_instance):
    """Seed the database with a test user."""
    with app_instance.app_context():

        username, password = os.getenv('TEST_USER'), os.getenv('TEST_PASSWORD')

        # make sure the environment variables are set
        if not (username and password):
            raise ValueError("Environment variables TEST_USER and TEST_PASSWORD must be set.")

        # create the test user
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(
                first_name="Test",
                last_name="User",
                username=username,
                password=generate_password_hash(password),
                shipping_address="123 Test St",
                billing_address="123 Test St",
                status="preferred",
                is_admin=True
            )
            db.session.add(user)
            db.session.commit()

    yield

    # clean up the database after tests
    with app_instance.app_context():
        if user:
            db.session.delete(user)
            db.session.commit()

# 3. Create a test client with a pre-logged-in user
@pytest.fixture(scope="module")
def client(app_instance, seed_database):
    """Return a test client with a pre-logged-in user session."""
    client = app_instance.test_client()
    
    # Fetch the test user and simulate login
    with app_instance.app_context():
        user = User.query.filter_by(username=os.getenv('TEST_USER')).first()
        
        if not user:
            raise ValueError("Test user not found in the database. Ensure seed_database runs successfully.")

    # Log in the user by setting the session user ID
    with client.session_transaction() as session:
        session['_user_id'] = user.id  # Flask-Login uses this to track logged-in users

    return client

# 4. Capture templates for testing
@pytest.fixture
def captured_templates(app_instance):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app_instance)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app_instance)


@pytest.fixture(scope="module")
def test_product(app_instance, client):
    """Seed the database with a test product."""

    # get the test user's user id
    user_id = User.query.filter_by(username=os.getenv('TEST_USER')).first().id

    with app_instance.app_context():
        product = Product(
            flavor="test",
            container_size="xlarge",
            price=10.00,
            quantity=10,
            committed_quantity=0,
            status="actual",
            dock_date=datetime.now().date(),
            user_id_add=user_id
        )
        db.session.add(product)
        db.session.commit()
        yield product
        db.session.delete(product)
        db.session.commit()
        
@pytest.fixture(scope="module")
def test_admin_config(app_instance):
    """Seed the database with test supported shipping types/costs."""

    with app_instance.app_context():
        auto_signoff_interval = AdminConfig(key='auto_signoff_interval_test', value='60', type='int')
        container_sizes = AdminConfig(key='supported_container_sizes_test', value='small,medium,large,xlarge', type='list')
        flavors = AdminConfig(key='supported_flavors_test', value='vanilla,chocolate,strawberry', type='list')
        shipping_types = AdminConfig(key='supported_shipping_types_test', value='standard,express', type='list')
        shipping_costs = AdminConfig(key='supported_shipping_costs_test', value='5.00,10.00', type='list')

        db.session.add(auto_signoff_interval)
        db.session.add(container_sizes)
        db.session.add(flavors)
        db.session.add(shipping_types)
        db.session.add(shipping_costs)
        db.session.commit()
        yield
        db.session.delete(auto_signoff_interval)
        db.session.delete(container_sizes)
        db.session.delete(flavors)
        db.session.delete(shipping_types)
        db.session.delete(shipping_costs)
        db.session.commit()

def pytest_html_report_title(report):
    report.title = "Frozen Assets Test Report"