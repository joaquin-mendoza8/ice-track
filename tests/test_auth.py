
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

def test_register_post_invalid_password(client, captured_templates):
    response = client.post('/register', data={
        "first-name": "Test",
        "last-name": "User",
        "username": "pytestuser",
        "password": "password",
        "confirm-password": "differentpassword",
        "shipping-address": "123 Test St",
        "billing-address": "123 Test St"
    })
    assert response.status_code == 200
    template, context = captured_templates[0]
    assert template.name == 'auth/register.html'

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