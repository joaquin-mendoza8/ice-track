import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

# load environment variables (local only)
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()
else:
    print("No .env file found, using CI environment variables.")


def test_logout(client, captured_templates):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    template, context = captured_templates[0]
    assert template.name == 'auth/login.html'


def test_login_post_success(client, captured_templates):

    username, password = os.getenv('TEST_USER'), os.getenv('TEST_PASSWORD')

    response = client.post('/login', data={
        "username": username,
        "password": password
    }, follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/inventory'
    template, context = captured_templates[0]
    assert template.name == 'inventory/inventory.html'


def test_login_post_invalid_password(client, captured_templates):
    response = client.post('/login', data={
        "username": os.getenv('TEST_USER'),
        "password": "invalidpassword"
    })
    assert response.status_code == 200
    template, context = captured_templates[0]
    assert template.name == 'auth/login.html'
    assert context['msg'] == "Invalid credentials provided."


def test_register_post_success(client, captured_templates):

    response = client.post('/register', data={
        "first-name": "Test",
        "last-name": "User",
        "username": "pytestuser",
        "password": "password123",
        "confirm-password": "password123",
        "shipping-address": "123 Test St",
        "billing-address": "123 Test St"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/login'
    template, context = captured_templates[0]
    assert template.name == 'auth/login.html'
    assert context['msg_type'] == 'success'


def test_register_post_user_exists(client, captured_templates):

    response = client.post('/register', data={
        "first-name": "Test",
        "last-name": "User",
        "username": "pytestuser",
        "password": "password",
        "confirm-password": "password",
        "shipping-address": "123 Test St",
        "billing-address": "123 Test St"
    })

    assert response.status_code == 400
    template, context = captured_templates[0]
    assert template.name == 'auth/register.html'
    assert context['msg'] == "User already exists."


def test_register_post_password_mismatch(client, captured_templates):

    response = client.post('/register', data={
        "first-name": "Test",
        "last-name": "User",
        "username": "pytestuser",
        "password": "password",
        "confirm-password": "password123",
        "shipping-address": "123 Test St",
        "billing-address": "123 Test St"
    })

    assert response.status_code == 200
    template, context = captured_templates[0]
    assert template.name == 'auth/register.html'
    assert context['msg'] == "Passwords do not match."


@pytest.mark.parametrize("password, expected", [
    ("p", "Password must be at least 8 characters long."),
    ("passwordpasswordpassword", "Password must be less than 20 characters long."),
    ("password123()", "Password can only contain numbers, letters, and special characters (!@#$%^&*-_+=).")
])
def test_register_post_invalid_password(client, captured_templates, password, expected):
    response = client.post('/register', data={
        "first-name": "Test",
        "last-name": "User",
        "username": "pytestuser",
        "password": password,
        "confirm-password": password,
        "shipping-address": "123 Test St",
        "billing-address": "123 Test St"
    })
    assert response.status_code == 200
    template, context = captured_templates[0]
    assert template.name == 'auth/register.html'
    assert context['msg'] == expected

# clean up the test user
def test_register_post_cleanup(app_instance):
    with app_instance.app_context():
        from app.models import User
        from app.extensions import db
        user = User.query.filter_by(username='pytestuser').first()
        if user:
            db.session.delete(user)
            db.session.commit()

        assert User.query.filter_by(username='pytestuser').first() is None

# GET REQUEST TESTS
def test_register_get(client):
    response = client.get('/register')
    assert response.status_code == 200

def test_login_get(client):
    response = client.get('/login')
    assert response.status_code == 200