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
    
    # relationship to Product (1-to-many)
    products_added = db.relationship('Product', foreign_keys='Product.user_id_add', backref='added_by', lazy=True)
    products_deleted = db.relationship('Product', foreign_keys='Product.user_id_delete', backref='deleted_by', lazy=True)

    # relationship to Product (1-to-many)
    products_added = db.relationship('Product', foreign_keys='Product.user_id_add', backref='added_by', lazy=True)
    products_deleted = db.relationship('Product', foreign_keys='Product.user_id_delete', backref='deleted_by', lazy=True)

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
    container_size=db.Column(db.String(50), primary_key=True) # a composite primary key for container sizes (small, medium, large)
    
    flavor=db.Column(db.String(150), nullable=False)
    price=db.Column(db.Float, nullable=False)
    quantity=db.Column(db.Integer, nullable=False)
    committed_quantity=db.Column(db.Integer, nullable=False, default=0) # quantity committed to orders
    status=db.Column(db.String(150), nullable=False, default='planned') # status of the product (planned or actual inventory)
    created_at=db.Column(db.DateTime, nullable=False, default=func.now()) # when the product was created
    deleted_at=db.Column(db.DateTime, nullable=True, default=None) # when the product was deleted
    dock_date=db.Column(db.Date, nullable=True) # when the product was/will be docked
    
    # create a link to User model to associate add/deletes to a user.
    user_id_add=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # user who added the product
    user_id_delete=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # user who deleted the product

    # 1:1 relationship between product & product_allocation
    allocation = db.relationship('ProductAllocation', backref='product', lazy=True, uselist=False)

    # print the product
    def __repr__(self):
        created_at_str = self.created_at.strftime('%m-%d-%Y %H:%S') if self.created_at else 'N/A'
        deleted_at_str = self.deleted_at.strftime('%m-%d-%Y %H:%S') if self.deleted_at else 'N/A'
        return f'<Product {self.flavor}, {self.container_size}, {created_at_str}, {deleted_at_str}>'
    
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

    
# Product allocation (to decouple products from inventory)
class ProductAllocation(db.Model):
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # foreign keys to Product and Order Item models
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_item.id'), nullable=False)

    # allocation attributes
    quantity_allocated = db.Column(db.Integer, nullable=False)
    disposition = db.Column(db.String(150), nullable=True)
    allocated_at = db.Column(db.DateTime, nullable=False, default=func.now())


    # 1:1 relationship between product_allocation and order_item
    # order_item = db.relationship('OrderItem', backref='allocation', lazy=True, uselist=False)

    # print the product allocation
    def __repr__(self):
        return (f'<ProductAllocation {self.id} for Product {self.product_id} => \
                order_items_id: {self.order_item_id}, quantity_allocated: {self.quantity_allocated}, \
                disposition: {self.disposition}>')
    
    # adjust the quantity of the product allocation and associated product
    def adjust_quantity(self, quantity_change):
        """
        Adjust the quantity of the product allocation and associated product.

        :param quantity_change: The amount to adjust the quantity by (positive or negative)
        """
        self.quantity_allocated += quantity_change
        self.product.adjust_quantity(-quantity_change, commit=True)


# Order Entry data model
class Order(db.Model):

    # defining data attributes in order
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # foreign key to User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # order shipment attributes
    # order shipment attributes
    shipping_type = db.Column(db.String(100), nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    expected_shipping_date = db.Column(db.Date, nullable=False) # expected date of shipping
    desired_receipt_date = db.Column(db.Date, nullable=False) # customer's desired date of receipt
    expected_shipping_date = db.Column(db.Date, nullable=False) # expected date of shipping
    desired_receipt_date = db.Column(db.Date, nullable=False) # customer's desired date of receipt
    shipping_address = db.Column(db.String(250), nullable=False)
    billing_address = db.Column(db.String(250), nullable=False)

    # order status/cost attributes
    created_at = db.Column(db.Date, nullable=False, default=func.now()) # date of order creation
    status = db.Column(db.String(150), nullable=False) # status of the order (e.g., "pending", "shipped", "delivered") TODO: maybe support cancelled
    payment_date = db.Column(db.Date, nullable=True) # date of payment

    # order status/cost attributes
    created_at = db.Column(db.Date, nullable=False, default=func.now()) # date of order creation
    status = db.Column(db.String(150), nullable=False) # status of the order (e.g., "pending", "shipped", "delivered") TODO: maybe support cancelled
    payment_date = db.Column(db.Date, nullable=True) # date of payment
    total_cost = db.Column(db.Float, nullable=False)

    # sets a one to many relationship with Order(one) and OrderItem(many)
    order_items = db.relationship('OrderItem', backref='parent_order', lazy=True, cascade="all, delete-orphan")
    order_items = db.relationship('OrderItem', backref='parent_order', lazy=True, cascade="all, delete-orphan")

    # 1:1 relationship with Shipment
    shipment = db.relationship('Shipment', backref='order', uselist=False, lazy=True)
    # 1:1 relationship with Shipment
    shipment = db.relationship('Shipment', backref='order', uselist=False, lazy=True)

    # print the order
    def __repr__(self):
        return f'<Order {self.id}>'
            
# Order item data models (products inside of an order)
class OrderItem(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # foreign keys
    # product_allocation_id = db.Column(db.Integer, db.ForeignKey('product_allocation.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

    # order item data attributes

    # foreign keys
    # product_allocation_id = db.Column(db.Integer, db.ForeignKey('product_allocation.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

    # order item data attributes
    quantity = db.Column(db.Integer, nullable=False)
    line_item_cost = db.Column(db.Float, nullable=False)

    # foreign keys to Order and Product models
    # parent_order = db.relationship('Order', backref='order_item', lazy=True)
    product = db.relationship('Product', backref='order_items', lazy=True)
    allocation = db.relationship('ProductAllocation', backref='order_item', lazy=True, cascade="all, delete-orphan")

    # print the order item
    def __repr__(self):
        return f'<OrderItem {self.id}, {self.product_id}, {self.order_id}, {self.quantity}, {self.line_item_cost}, {self.allocation}>'
    # parent_order = db.relationship('Order', backref='order_item', lazy=True)
    product = db.relationship('Product', backref='order_items', lazy=True)
    allocation = db.relationship('ProductAllocation', backref='order_item', lazy=True, cascade="all, delete-orphan")

    # print the order item
    def __repr__(self):
        return f'<OrderItem {self.id}, {self.product_id}, {self.order_id}, {self.quantity}, {self.line_item_cost}, {self.allocation}>'
    

# Admin Configuration Settings data model
class AdminConfig(db.Model):


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # configuration attributes

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
    date_shipped = db.Column(db.Date, nullable=False, default=func.now())
    shipment_boxes = db.Column(db.Integer, nullable=False)
    partial_delivery = db.Column(db.Boolean, nullable=False, default=False)
    estimated_delivery_date = db.Column(db.Date, nullable=False)
    actual_delivery_date = db.Column(db.Date, nullable=True)
    shipment_type = db.Column(db.String(150), nullable=False)

    # loss and damage shipment attributes
    lost_or_damaged = db.Column(db.Boolean, nullable=False, default=False)
    problem_description = db.Column(db.String(500), nullable=False, default="No issues")
    shipping_vendor = db.Column(db.String(150), nullable=False, default="Unknown Vendor")
    damage_cost = db.Column(db.Float, nullable=False, default=0.0)

    # print the shipment
    def __repr__(self):
        return f'<Shipment {self.id}>'
    
# Logging Data Model
class Log(db.Model):
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # log attributes
    action = db.Column(db.String(50), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    container_size = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=func.now())

    # Many:1 relationship with User
    user = db.relationship('User', backref='logs', lazy=True)
    
# Logging Data Model
class Log(db.Model):
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # log attributes
    action = db.Column(db.String(50), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    container_size = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=func.now())

    # Many:1 relationship with User
    user = db.relationship('User', backref='logs', lazy=True)
