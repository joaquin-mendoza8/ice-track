# DATA MODELS FOR THE APPLICATION
# Contains classes for the data models used in the application. Each class corresponds
from app.extensions import db
from sqlalchemy.sql import func
from flask_login import UserMixin

# User class
class User(db.Model, UserMixin):

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    # relationship to Order (1-to-many)
    orders = db.relationship('Order', backref='user', lazy=True)
    
    # print the user
    def __repr__(self):
        return f'<User {self.username}>'
    
    # get the user id (for flask-login)
    def get_id(self):
        return self.id

# Ice Cream data model TODO: decouple from inventory
class Product(db.Model):

    # composite primary key (id, container_size) to reflect unique product per container size
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    container_size=db.Column(db.String(50))
    flavor=db.Column(db.String(150), nullable=False)
    price=db.Column(db.Float, nullable=False)
    quantity=db.Column(db.Integer, nullable=False)
    committed_quantity=db.Column(db.Integer, nullable=False, default=0) # quantity committed to orders
    status=db.Column(db.String(150), nullable=False, default='planned') # status of the product (planned or actual inventory)
    created_at=db.Column(db.DateTime, nullable=False, default=func.now()) # when the product was created
    deleted_at=db.Column(db.DateTime, nullable=True, default=None) # when the product was deleted
    disposition=db.Column(db.String(150), nullable=True)  # disposition of a removed product (shipped, defective, spoiled, etc.)
    
    # create a link to User model to associate add/deletes to a user.
    user_id_add=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # user who added the product
    user_id_delete=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # user who deleted the product
    
    # relationship to OrderItem (1-to-many)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    # print the product
    def __repr__(self):
        return f'<Product {self.flavor}>'
    
    def adjust_quantity(self, quantity_change, commit=False):
        """
        Adjust the quantity and committed_quantity of the product.

        :param quantity_change: The amount to adjust the quantity by (positive or negative)
        :param commit: Whether to commit the changes to the database
        """
        self.quantity += quantity_change
        if commit:
            self.committed_quantity += -quantity_change
        db.session.add(self)
        db.session.commit()


# Order Entry data model
class Order(db.Model):

    # defining data attributes in order
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # foreign key to User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # order shipment attributes
    shipping_type = db.Column(db.String(100), nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    expected_shipping_date = db.Column(db.Date, nullable=False) # expected date of shipping
    desired_receipt_date = db.Column(db.Date, nullable=False) # customer's desired date of receipt
    shipping_address = db.Column(db.String(250), nullable=False)
    billing_address = db.Column(db.String(250), nullable=False)

    # order status/cost attributes
    created_at = db.Column(db.Date, nullable=False, default=func.now()) # date of order creation
    status = db.Column(db.String(150), nullable=False) # status of the order (e.g., "pending", "shipped", "delivered") TODO: maybe support cancelled
    payment_date = db.Column(db.Date, nullable=True) # date of payment
    total_cost = db.Column(db.Float, nullable=False)

    # sets a one to many relationship with Order(one) and OrderItem(many)
    order_items = db.relationship('OrderItem', backref='parent_order', lazy=True, cascade="all, delete-orphan")

    # 1:1 relationship with Shipment
    shipment = db.relationship('Shipment', backref='order', uselist=False, lazy=True)

    # print the order
    def __repr__(self):
        return f'<Order {self.id}>'
            
# Order item data models (products inside of an order)
class OrderItem(db.Model):

    # order item data attributes
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer, nullable=False)
    line_item_cost = db.Column(db.Float, nullable=False)

    # foreign keys to Order and Product models
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    

# Admin Configuration Settings data model
class AdminConfig(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # configuration attributes
    key = db.Column(db.String(50), nullable=False) # e.g., "supported_container_sizes"
    value = db.Column(db.Text, nullable=False) # store JSON data as text
    type = db.Column(db.String(50), nullable=False) # e.g., "list", "dict", "str", "int", "float"

    # print the admin configuration
    def __repr__(self):
        return f'<AdminConfig {self.id}>'

class Shipment(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # shipment attributes
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    date_shipped = db.Column(db.Date, nullable=False)
    shipment_boxes = db.Column(db.Integer, nullable=False)
    partial_delivery = db.Column(db.Boolean, nullable=False, default=False)
    estimated_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    shipment_type = db.Column(db.String(150), nullable=False)

    # print the shipment
    def __repr__(self):
        return f'<Shipment {self.id}>'
