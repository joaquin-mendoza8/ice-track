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

    # composite primary key (id, container_size) to reflect unique product per container size
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    container_size=db.Column(db.String(50), primary_key=True) # a composite primary key for container sizes (small, medium, large)
    
    flavor=db.Column(db.String(150), nullable=False)
    price=db.Column(db.Float, nullable=False)
    quantity=db.Column(db.Integer, nullable=False)
    status=db.Column(db.String(150), nullable=False, default='planned') # status of the product (planned or actual inventory)
    created_at=db.Column(db.DateTime, nullable=False, default=func.now()) # when the product was created
    deleted_at=db.Column(db.DateTime, nullable=True, default=None) # when the product was deleted
    disposition=db.Column(db.String(150), nullable=True)  # disposition of a removed product (shipped, defective, spoiled, etc.)
    
    # create a link to User model to associate add/deletes to a user.
    user_id_add=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # user who added the product
    user_id_delete=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # user who deleted the product
    
    
    # order_id=db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True) # TODO: implement after orders are implemented

    # print the product
    def __repr__(self):
        return f'<Product {self.flavor}>'


# Order Entry data model
class Order(db.Model):

    # defining data attributes in order
    id = db.Column(db.Integer, primary_key= True)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_status = db.Column(db.String(50), nullable=False)
    shipping_address = db.Column(db.String(150), nullable=False)
    shipping_type = db.Column(db.String(100), nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    billing_address = db.Column(db.String(150), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

    # sets a one to many relationship with Order(one) and OrderItem(many)
    orders_items = db.relationship('OrderItem', backref='order')
    # initializing each attribute
    def __init__(self, customer_name, customer_status, shipping_address, 
                 shipping_type, shipping_cost, billing_address, total_cost):
        self.customer_name = customer_name
        self.customer_status = customer_status
        self.shipping_address = shipping_address
        self.shipping_type = shipping_type
        self.shipping_cost = shipping_cost
        self.billing_address = billing_address
        self.total_cost = total_cost

# Order item data models (products inside of an order)
class OrderItem(db.Model):
    #defining product data attributes
    id = db.Column(db.Integer, primary_key= True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    ship_date = db.Column(db.Date, nullable=False)

    # sets a one to many relationship with OrderItem(one) and product(many) 
    product = db.relationship('Product', backref='order_items')
    # sets a many to one relationship with OrderItem(many) and order(one)
    order = db.relationship('Order', backref='order_items')

    # initializing attributes
    def __init__(self, order_id, product_id, quantity, ship_date):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.ship_date = ship_date
        
