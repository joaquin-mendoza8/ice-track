# DATA MODELS FOR THE APPLICATION
# Contains classes for the data models used in the application. Each class corresponds
from config.config import db
from datetime import datetime

# User class
class User(db.Model):

    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(150), unique=True, nullable=False)
    password=db.Column(db.String(150), nullable=False)
    is_active=db.Column(db.Boolean, default=True)
    last_login=db.Column(db.DateTime, nullable=True, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __repr__(self):
        return f'<User {self.username}>'