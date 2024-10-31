
def parse_product_data(products):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {"id": product.id, "flavor": product.flavor, 
         "price": product.price, "quantity": product.quantity,
         "status": product.status, "created_at": product.created_at}
        for product in products
    ]
