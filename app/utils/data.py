
def parse_product_data(products):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {"id": product.id, "flavor": product.flavor, 
         "price": product.price, "quantity": product.quantity,
         "status": product.status}
        for product in products
    ]

def parse_order_data(orders):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {"id": order.id, "customer_name": order.customer_name, 
         "customer_status": order.customer_status, 
         "shipping_address": order.shipping_address, 
         "shipping_type": order.shipping_type, 
         "shipping_cost": order.shipping_cost, 
         "billing_address": order.billing_address, 
         "total_cost": order.total_cost}
        for order in orders
    ]