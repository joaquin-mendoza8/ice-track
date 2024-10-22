
def parse_product_data(products):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {"id": product.id, "flavor": product.flavor, "price": product.price, "quantity": product.quantity}
        for product in products
    ]
