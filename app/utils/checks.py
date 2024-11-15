
from app.models import Product


def check_container_sizes_in_use(container_sizes_list):
    """
    Check if any container sizes exist in non-deleted products in the inventory.

    Args:
        container_sizes_list (list): List of container sizes to check.

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