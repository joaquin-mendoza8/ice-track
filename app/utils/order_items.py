from app.extensions import db
from app.models import Product, ProductAllocation, Order, OrderItem
from datetime import datetime


def extract_order_items(request_form):
    """
    Extracts order line-item data into a list 
    of dictionaries from a form request.
    """
    order_items_data = []
    for key in request_form:
        if key.startswith('order_items'):
            index = int(key.split('[')[1].split(']')[0])
            item_key = key.split('[')[2].split(']')[0].replace('-', '_')
            if len(order_items_data) <= index:
                order_items_data.append({})
            value = request_form.get(key)
            if item_key == 'quantity':
                value = int(value)
            elif item_key == 'line_item_cost':
                value = float(value)
            order_items_data[index][item_key] = value

    return order_items_data

def extract_relevant_values(order_item, keys):
    """Extracts relevant values from the order item based on the specified keys."""
    return {key: order_item.get(key) for key in keys}

def compare_order_items(order_item1, order_item2, keys):
    """Compares specific values of two order items for equality."""
    values1 = extract_relevant_values(order_item1, keys)
    values2 = extract_relevant_values(order_item2, keys)
    return values1 == values2

def create_order_item(order_item_request, order_id):
    """
    Create a new order item and associated product allocation 
    given an order item list of dictionaries
    """
    if not order_item_request:
        return "Error creating new order item. Order item request string is empty"

    flavor = order_item_request.get('flavor')
    container_size = order_item_request.get('container_size')
    quantity = int(order_item_request.get('quantity'))
    line_item_cost = float(order_item_request.get('line_item_cost'))

    # get the product id
    product = Product.query.filter_by(
        flavor=flavor, container_size=container_size, deleted_at=None).first()

    product_id = None
    if product:
        product_id = product.id
    else:
        return "Product not found"

    # create the order item
    order_item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        line_item_cost=line_item_cost
    )
    db.session.add(order_item)
    db.session.flush()

    # create a product allocation
    product_allocation = ProductAllocation(
        product_id=product_id,
        order_item_id=order_item.id,
        quantity_allocated=0,
        disposition='committed',
        allocated_at=datetime.now()
    )
    db.session.add(product_allocation)
    db.session.flush()

    # adjust the quantity of the product allocation and product
    product_allocation.adjust_quantity(quantity)