from flask_session import Session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# initialize extensions without binding to app
db = SQLAlchemy()
flask_session = Session()
migrate = Migrate()
login_manager = LoginManager()