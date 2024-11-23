
from app.models import Product, Order


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