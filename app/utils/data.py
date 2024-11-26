
def parse_product_data(products):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {
            "id": product.id,
            "flavor": product.flavor,
            "container_size": product.container_size,
            "price": product.price,
            "quantity": product.quantity,
            "committed_quantity": product.committed_quantity,
            "status": product.status
        }
        for product in products
    ]

def parse_order_data(orders):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {
            "id": order.id,
            "customer": f'{order.user.first_name} {order.user.last_name}',
            "order_creation_date": order.created_at,
            "shipping_address": order.shipping_address, 
            "billing_address": order.billing_address,
            "shipping_type": order.shipping_type, 
            "expected_shipping_date": order.expected_shipping_date,
            "desired_receipt_date": order.desired_receipt_date,
            "shipping_cost": order.shipping_cost, 
            "billing_address": order.billing_address,
            "status": order.status,
            "line_item_costs": [item.line_item_cost for item in order.order_items],
            "line_items": [item for item in order.order_items], 
            "total_cost": order.total_cost
        }
        for order in orders
    ]

def parse_order_item_data(order_items):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {
            "id": order_item.id,
            "quantity": order_item.quantity,
            "line_item_cost": order_item.line_item_cost,
            "product_id": order_item.product_id,
            "flavor": order_item.product.flavor,
            "container_size": order_item.product.container_size,
            "price": order_item.product.price,
            "order_id": order_item.order_id,
        }
        for order_item in order_items
    ]

def parse_customer_data(customers):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {
            "id": customer.id,
            "name": f"{customer.first_name} {customer.last_name}",
            "status": customer.status,
            "shipping_address": customer.shipping_address,
            "billing_address": customer.billing_address,
        }
        for customer in customers
    ]

def parse_admin_config_data(configs):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {
            "id": config.id, 
            "key": config.key, 
            "value": config.value,
            "type": config.type
        }
        for config in configs
    ]

def parse_shipment_data(shipments):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {
            "id": shipment.id,
            "order_id": shipment.order_id,
            "date_shipped": shipment.date_shipped,
            "shipment_boxes": shipment.shipment_boxes,
            "partial_delivery": shipment.partial_delivery,
            "estimated_date": shipment.estimated_date,
            "delivery_date": shipment.delivery_date,
            "shipment_type": shipment.shipment_type,
        }
        for shipment in shipments
    ]