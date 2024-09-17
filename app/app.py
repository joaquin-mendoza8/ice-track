from flask import Flask, request, jsonify, render_template
from flask_session import Session as flask_session
from flask_migrate import Migrate
from flask_login import LoginManager
from config.config import Config, db, session as flask_session
from app.endpoints.auth import auth
from app.models import User

# create the flask app
app = Flask(__name__, template_folder='public/templates', static_folder='public/static')

# configure the flask app
app.config.from_object(Config)
db.init_app(app)
flask_session.init_app(app)
migrate = Migrate(app, db)

# connect blueprints
# app.register_blueprint(<BLUEPRINT_NAME>)
app.register_blueprint(auth)

# create the database tables
with app.app_context():
    db.create_all()

# init flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# create the home endpoint
@app.route('/')
def home():
    return render_template('home.html')



