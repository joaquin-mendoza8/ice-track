# DATA MODELS FOR THE APPLICATION
# Contains classes for the data models used in the application. Each class corresponds
from app.extensions import db
from sqlalchemy.sql import func
from flask_login import UserMixin

# User class
class User(db.Model, UserMixin):

    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(150), unique=True, nullable=False)
    password=db.Column(db.String(150), nullable=False)
    last_login=db.Column(db.DateTime, nullable=True, default=func.now())    # automatically set to current time for new users
    is_admin=db.Column(db.Boolean, default=False)   # automatically set to False for new users

    # customer-related fields
    first_name=db.Column(db.String(150), nullable=False) # customer first name
    last_name=db.Column(db.String(150), nullable=False) # customer last name
    status=db.Column(db.String(150), nullable=False) # preferred, ok, shaky
    shipping_address=db.Column(db.String(250), nullable=False)
    billing_address=db.Column(db.String(250), nullable=False)
    
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
    container_size=db.Column(db.String(50))
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

    # foreign keys to User model
    customer_first_name = db.ForeignKey('user.first_name')
    customer_last_name = db.ForeignKey('user.last_name')
    customer_status = db.ForeignKey('user.status')
    shipping_address = db.ForeignKey('user.shipping_address')
    billing_address = db.ForeignKey('user.billing_address')

    # order data attributes
    shipping_type = db.Column(db.String(100), nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    billing_address = db.Column(db.String(150), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

    # sets a one to many relationship with Order(one) and OrderItem(many)
    order_items = db.relationship('OrderItem', backref='parent_order', lazy=True)

    # print the order
    def __repr__(self):
        return f'<Order {self.id}>'
            
# Order item data models (products inside of an order)
class OrderItem(db.Model):
    #defining product data attributes
    id = db.Column(db.Integer, primary_key= True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    ship_date = db.Column(db.Date, nullable=False)

    # sets a one to many relationship with OrderItem(one) and product(many) 
    # product = db.relationship('Product', backref='order_item')
    # sets a many to one relationship with OrderItem(many) and order(one)
    # order = db.relationship('Order', backref='order_item')

    # initializing attributes
    def __init__(self, order_id, product_id, quantity, ship_date):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.ship_date = ship_date
    
        
# Admin Configuration Settings data model
class AdminConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False) # e.g., "supported_container_sizes"
    value = db.Column(db.Text, nullable=False) # store JSON data as text
    type = db.Column(db.String(50), nullable=False) # e.g., "list", "dict", "str", "int", "float"

    # print the admin configuration
    def __repr__(self):
        return f'<AdminConfig {self.id}>'
