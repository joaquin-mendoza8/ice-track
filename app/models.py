# DATA MODELS FOR THE APPLICATION
# Contains classes for the data models used in the application. Each class corresponds
from config.config import db
from sqlalchemy.sql import func
from flask_login import UserMixin

# User class
class User(db.Model, UserMixin):

    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(150), unique=True, nullable=False)
    password=db.Column(db.String(150), nullable=False)
    is_active=db.Column(db.Boolean, default=True)   # automatically set to True for new users
    last_login=db.Column(db.DateTime, nullable=True, default=func.now())    # automatically set to current time for new users

    # print the user
    def __repr__(self):
        return f'<User {self.username}>'
    
    # get the user id (for flask-login)
    def get_id(self):
        return self.id