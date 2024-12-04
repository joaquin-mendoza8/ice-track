
from app.models import Product, Order, Shipment
from datetime import datetime, timedelta
from app.extensions import db


def check_container_sizes_in_use(container_sizes_list):
    """
    Before deleting a container size, check if it is in use by any products in the inventory.

    Args:
        container_sizes_list (list): List of container sizes that were passed in the request.

    Returns:
        list: List of container sizes that are in use.
    """
    # get all currently existing container sizes from the products table
    container_sizes_in_inventory = Product.query.with_entities(Product.container_size).filter(Product.deleted_at.is_(None)).distinct().all()
    container_sizes_in_inventory = [size[0] for size in container_sizes_in_inventory] if container_sizes_in_inventory else []

    # list of container sizes in use (in inventory)
    container_sizes_in_use = []

    # check if any container sizes are in use
    for size in container_sizes_list:
        if size in container_sizes_in_inventory:
            container_sizes_in_use.append(size)

    return container_sizes_in_use


def check_flavors_in_use(supported_flavors_list):
    """
    Before deleting a flavor, check if it is in use by any products in the inventory.

    Args:
        supported_flavors_list (list): List of flavors that were passed in the request.

    Returns:
        list: List of flavors that are in use.
    """
    # get all currently existing flavors from the products table
    flavors_in_inventory = Product.query.with_entities(Product.flavor).filter(Product.deleted_at.is_(None)).distinct().all()
    flavors_in_inventory = [flavor[0] for flavor in flavors_in_inventory] if flavors_in_inventory else []

    # list of flavors in use (in inventory)
    flavors_in_use = []

    # check if any flavors are in use
    for flavor in supported_flavors_list:
        if flavor in flavors_in_inventory:
            flavors_in_use.append(flavor)

    return flavors_in_use

def check_shipping_types_in_use(supported_shipping_types_list):
    """
    Before deleting a shipping type, check if it is in use by any orders in the database.

    Args:
        supported_shipping_types_list (list): List of shipping types that were passed in the request.

    Returns:
        list: List of shipping types that are in use.
    """
    # get all currently existing shipping types from the orders table
    shipping_types_in_orders = Order.query.with_entities(Order.shipping_type).distinct().all()
    shipping_types_in_orders = [shipping_type[0] for shipping_type in shipping_types_in_orders] if shipping_types_in_orders else []

    # list of shipping types in use (in orders)
    shipping_types_in_use = []

    # check if any shipping types are in use
    for shipping_type in supported_shipping_types_list:
        if shipping_type in shipping_types_in_orders:
            shipping_types_in_use.append(shipping_type)

    return shipping_types_in_use

def check_customer_order_limit(customer_status):
    """
    Check what the customer's order limit is.

    Args:
        customer_status (str): Customer status.

    Returns:
        int: Customer's order limit ($).
    """

    if customer_status == "preferred":
         return None
    elif customer_status == "ok":
        return 3000
    else:
        return 500
    

def check_inventory_update(product, request_data):
    """
    Check if there are any missing fields, if the product exists, if any fields have changed,
    and if any fields are less than or equal to zero.

    Args:
        product (Product): Product object.
        request_data (dict): Request data.

    Returns:
        tuple: Message and message type
    """

    try:

        # unpack request data
        product_id = request_data.get('product_id')
        product_flavor = request_data.get('product_flavor')
        product_container_size = request_data.get('product_container_size')
        product_price = request_data.get('product_price')
        product_quantity = request_data.get('product_quantity')
        product_status = request_data.get('product_status')
        product_dock_date = request_data.get('product_dock_date')

        # check if any field is missing
        if not all([product_id, product_flavor, product_container_size,
                product_price, product_quantity, product_status,
                product_dock_date]
        ):
            return "Missing fields", "danger"
        
        # check if product exists
        if not product:
            return "Product not found", "danger"

        # check if any of the fields have changed
        if all([
                product.flavor == product_flavor,
                product.container_size == product_container_size,
                product.price == float(product_price),
                product.quantity == int(product_quantity),
                product.status == product_status,
                product.dock_date.strftime('%Y-%m-%d') == datetime.strptime(product_dock_date, '%m/%d/%Y').strftime('%Y-%m-%d')
        ]):
            return "No changes detected", "info"
        
        # check if any of the fields are less than or equal to zero
        if any([
                float(product_price) <= 0,
                int(product_quantity) <= 0
        ]):
            return "Price and quantity must be greater than zero", "danger"
        
        # check if the dock date is in the past, but the status is not set to 'actual'
        if (datetime.strptime(product_dock_date, '%m/%d/%Y').date() < datetime.now().date()
            and product_status != 'actual'):
            return "If the dock date is in the past, the status must be set to 'actual'", "danger"
        
        # check if the dock date is set to a date in the future, but the status is not set to 'planned'
        if (datetime.strptime(product_dock_date, '%m/%d/%Y').date() > datetime.now().date()
            and product_status != 'planned'):
            return "If the dock date is in the future, the status must be set to 'planned'", "danger"
        
        # check if the flavor and container size are the same as another product in the inventory but price is different
        existing_product = Product.query.filter_by(flavor=product_flavor, container_size=product_container_size).first()
        if existing_product and (existing_product.price != float(product_price)):
            return "A product with the same flavor and container size already exists but with a different price", "danger"

        # no issues
        return None, None
    
    except Exception as e:
        print(e)
        return "An error occurred while running input validation", "danger"

    
def remove_expired_shipments():
    """Remove any shipments with delivery/payment date > 30 days"""

    try:

        shipments = Shipment.query.all()

        # delete any old shipments TODO: finish comparing actual/now date, payment/now date
        for shipment in shipments:
            delivery_date_diff, payment_date_diff = None, None

            # compute date diffs
            if shipment.actual_delivery_date:
                delivery_date_diff = shipment.actual_delivery_date - datetime.now().date()
            if shipment.order.payment_date:
                payment_date_diff = shipment.order.payment_date - datetime.now().date()

            # both diffs present
            if (
                (delivery_date_diff and delivery_date_diff > timedelta(days=30)) or
                (payment_date_diff and payment_date_diff > timedelta(days=30))
            ):
                db.session.delete(shipment)

        # commit any changes
        if db.session.dirty:
            db.session.commit()

    except Exception as e:
        print(e)
        db.session.rollback()


def update_committed_quantities(products):
    """
    Update committed quantities for all products in the inventory
    by summing the allocations for each product.
    """

    try:

        # update committed quantities
        for product in products:

            # sum the allocations for each product
            new_committed_quantity = 0
            for allocation in product.allocations:
                new_committed_quantity += allocation.quantity_allocated

            # check if committed quantity has changed
            if new_committed_quantity != product.committed_quantity:
                # update committed quantity
                product.committed_quantity = new_committed_quantity

        # commit any changes
        if db.session.dirty:
            db.session.commit()

    except Exception as e:
        msg = "Error updating committed quantities."
        print(msg + f': {e}')
        db.session.rollback()