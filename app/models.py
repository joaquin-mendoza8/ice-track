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

    #TODO: Add customer status column
    
    # print the user
    def __repr__(self):
        return f'<User {self.username}>'
    
    # get the user id (for flask-login)
    def get_id(self):
        return self.id


# Ice Cream data model
class Product(db.Model):

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    flavor=db.Column(db.String(150), nullable=False)
    price=db.Column(db.Float, nullable=False)
    quantity=db.Column(db.Integer, nullable=False)
    status=db.Column(db.String(150), nullable=False, default='planned') # status of the product (planned or actual inventory)
    created_at=db.Column(db.DateTime, nullable=False, default=func.now()) # when the product was created
    deleted_at=db.Column(db.DateTime, nullable=True, default=None) # when the product was deleted
    disposition=db.Column(db.String(150), nullable=True)  # disposition of a removed product (shipped, defective, spoiled, etc.)
    # unit_size=db.Column(db.String(150), nullable=False) # TODO: figure out how to implement this
    # order_id=db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True) # TODO: implement after orders are implemented

    # print the product
    def __repr__(self):
        return f'<Product {self.flavor}>'
'''    
class Order(db.Model):
    
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    flavor=db.Column(db.String(150), nullable=False)
    size=db.Column(db.String(150), nullable=False)
    quantity=db.Column(db.Integer, nullable=False)
    cost=db.Column(db.Integer, nullable=False)
    shipping_type=db.Column(db.String(250), nullable=False)
    shipping_date=db.Column(db.Date, nullable=False)
    shipping_cost=db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<Customer {self.name}>'
'''

'''
class Customer(db.Model):
    
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    name=db.Column(db.String(150), nullable=False)
    status=db.Column(db.String(150), nullable=False)
    shipping_address=db.Column(db.String(250), nullable=False)
    billing_address=db.Column(db.String(250), nullable=False)
    
    def __repr__(self):
        return f'<Customer {self.name}>'
'''   
