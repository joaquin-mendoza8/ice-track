
# The series of functions below converts a SQLAlchemy list of objects to a dictionary

def parse_product_data(products):    
    return [
        {"id": product.id, "flavor": product.flavor, 
         "price": product.price, "quantity": product.quantity,
         "status": product.status}
        for product in products
    ]
    
# TODO: Add more fields from Order when neccesary
def parse_order_data(orders):
    return [
        {   "id": order.id,
            "customer_name": order.customer_name,
            "shipping_address": order.shipping_address,
            "total_cost": order.total_cost,
            "order_items": order.order_items
        }
        for order in orders
    ]

def parse_customer_data(customers):
    return [
        {
            "id": customer.id,
            "name": customer.name,
            "status": customer.status,
            "shipping_address": customer.shipping_address,
            "billing_address": customer.billing_address
        }
        for customer in customers
    ]