from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_session import Session as flask_session
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from config.config import Config, db, session as flask_session
from app.utils.filters import *
from app.endpoints.auth import auth
from app.endpoints.inventory import inventory
from app.endpoints.orders import orders
from app.endpoints.shipments import shipments
from app.endpoints.tickets import tickets
from app.models import User, Order, Customer, Product
from sqlalchemy import text

# create the flask app
app = Flask(__name__)

# configure the flask app
app.config.from_object(Config)
db.init_app(app)
flask_session.init_app(app)
migrate = Migrate(app, db)

# register all custom Jinja filters
filters = globals().copy()
for name, func in filters.items():
    if callable(func) and name.startswith('format_'):
        app.jinja_env.filters[name.split('format_')[1]] = func

# connect blueprints
# app.register_blueprint(<BLUEPRINT_NAME>)
app.register_blueprint(auth)
app.register_blueprint(inventory)
app.register_blueprint(orders)
app.register_blueprint(shipments)
app.register_blueprint(tickets)

# create the database tables
with app.app_context():
    db.create_all()

# init flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# create the home endpoint
@app.route('/')
@login_required
def home():
    # if user is not logged in, redirect to login
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('home.html')





