
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
            "status": product.status,
            "dock_date": product.dock_date.strftime('%m/%d/%Y') if product.dock_date else None,
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
    
    # return [
    #     {
    #         "id": order_item.id,
    #         "quantity": order_item.quantity,
    #         "line_item_cost": order_item.line_item_cost,
    #         "flavor": order_item.allocation[0].product.flavor,
    #         "flavor": order_item.allocation[0].product.flavor,
    #         "container_size": order_item.allocation[0].product.container_size,
    #         "price": order_item.allocation[0].product.price,
    #         "order_id": order_item.order_id,
    #     }
        
    # ]
    parsed = []
    for order_item in order_items:
        parsed.append(
            {
                "id": order_item.id,
                "quantity": order_item.quantity,
                "line_item_cost": order_item.line_item_cost,
                "order_id": order_item.order_id,
            }
        )

        if order_item.allocation:
            parsed[-1].update(
                {
                    "flavor": order_item.allocation[0].product.flavor,
                    "container_size": order_item.allocation[0].product.container_size,
                    "price": order_item.allocation[0].product.price,
                }
            )


def parse_product_allocation_data(product_allocations):
    """Converts a SQLAlchemy list of objects to a dictionary"""

    return [
        {
            "id": product_allocation.id,
            "product_id": product_allocation.product_id,
            "order_item_id": product_allocation.order_item_id,
            "quantity_allocated": product_allocation.quantity_allocated,
            "disposition": product_allocation.disposition,
            "allocated_at": product_allocation.allocated_at,
            "product": product_allocation.product
        }
        for product_allocation in product_allocations
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