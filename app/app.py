from flask import Flask
from app.extensions import db, migrate, login_manager, flask_session
from config.config import Config, DevelopmentConfig, TestConfig, ProductionConfig


def create_app(config_class=Config):
    """Application factory function."""

    # create the flask app
    app = Flask(__name__)

    # load the app configuration
    app.config.from_object(config_class)

    # initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Conditionally initialize Flask-Session
    if app.config['SESSION_TYPE'] == 'sqlalchemy':
        app.config['SESSION_SQLALCHEMY'] = db  # Link Flask-Session with SQLAlchemy
        flask_session.init_app(app)  # Initialize with only app
    else:
        flask_session.init_app(app)

    # configure the login manager (required by flask-login)
    login_manager.login_view = 'auth.login'

    # register blueprints
    from app.endpoints.auth import auth
    from app.endpoints.inventory import inventory
    from app.endpoints.order import orders
    from app.endpoints.shipments import shipments
    from app.endpoints.tickets import tickets
    from app.endpoints.admin import admin
    from app.endpoints.home import home

    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(inventory)
    app.register_blueprint(orders)
    app.register_blueprint(shipments)
    app.register_blueprint(tickets)
    app.register_blueprint(home)

    # register all custom Jinja filters
    from app.utils.filters import format_currency, format_currency_list, format_date, format_attribute, format_address

    app.jinja_env.filters['currency'] = format_currency
    app.jinja_env.filters['currency_list'] = format_currency_list
    app.jinja_env.filters['date'] = format_date
    app.jinja_env.filters['attribute'] = format_attribute
    app.jinja_env.filters['address'] = format_address

    # create the database tables
    with app.app_context():
        db.create_all()

    # user loader for login manager (required by flask-login)
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        """
        Flask-Login user loader callback.
        Loads a user from the database by ID.
        """
        return User.query.get(int(user_id))

    return app





