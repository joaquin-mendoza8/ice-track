import pytest
import os
import sys
from werkzeug.security import generate_password_hash


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import create_app
from config.config import TestConfig
from app.models import User
from app.extensions import db

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
                status="preferred"
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