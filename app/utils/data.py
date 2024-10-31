
# The series of functions below converts a SQLAlchemy list of objects to a dictionary

def parse_product_data(products):    
    return [
        {"id": product.id, "flavor": product.flavor, 
         "price": product.price, "quantity": product.quantity,
         "status": product.status, "created_at": product.created_at}
        for product in products
    ]
    
def parse_orders_data(orders):
    return [
        {   "id": order.id,
            "flavor": order.flavor,
            "size": order.size,
            "quantity": order.quantity,
            "cost": order.cost,
            "shipping_type": order.shipping_type,
            "shipping_date": order.shipping_date.strftime('%Y-%m-%d'),
            "shipping_cost": order.shipping_cost
        }
        for order in orders
    ]

def parse_customers_data(customers):
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