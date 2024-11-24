
def parse_product_data(products):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {
            "id": product.id,
            "flavor": product.flavor,
            "container_size": product.container_size,
            "price": product.price,
            "quantity": product.quantity,
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
            "shipping_address": order.shipping_address, 
            "billing_address": order.billing_address,
            "shipping_type": order.shipping_type, 
            "shipping_date": order.shipping_date,
            "shipping_cost": order.shipping_cost, 
            "billing_address": order.billing_address, 
            "total_cost": order.total_cost
        }
        for order in orders
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
            "shipment_boxes": shipment.shippment_boxes,
            "partial_delivery": shipment.partial_delivery,
            "estimated_date": shipment.estimated_date,
            "delivery_date": shipment.delivery_date,
            "shipment_type": shipment.shippment_type,
        }
        for shipment in shipments
    ]