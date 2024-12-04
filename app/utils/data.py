
def format_date(date):
    """Converts a date to a more readable string."""
    
    return date.strftime('%m/%d/%Y') if date else None


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
            "dock_date": product.dock_date,
        }
        for product in products
    ]

def parse_order_data(orders):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "invoice_id": order.invoice[0].id if order.invoice else None,
            "customer": f'{order.user.first_name} {order.user.last_name}',
            "order_creation_date": order.created_at,
            "shipping_address": order.shipping_address, 
            "billing_address": order.billing_address,
            "shipping_type": order.shipping_type, 
            "expected_shipping_date": order.expected_shipping_date,
            "desired_receipt_date": order.desired_receipt_date,
            "payment_date": order.payment_date or None,
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

    return parsed


def parse_product_allocation_data(product_allocations):
    """Converts a SQLAlchemy list of objects to a dictionary"""

    return [
        {
            "product": product_allocation.product,
            "order_item": product_allocation.order_item,
            "flavor": product_allocation.product.flavor,
            "container_size": product_allocation.product.container_size,
            "price": product_allocation.product.price,
            "id": product_allocation.id,
            "product_id": product_allocation.product_id,
            "order_item_id": product_allocation.order_item_id,
            "quantity_allocated": product_allocation.quantity_allocated,
            "shipment_id": product_allocation.shipment_id,
            "order_id": product_allocation.order_id,
            "disposition": product_allocation.disposition,
            "allocated_at": product_allocation.allocated_at,
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
            "user_id": shipment.user_id,
            "order_id": shipment.order_id,
            "order": shipment.order,
            "date_shipped": shipment.date_shipped,
            "estimated_delivery_date": shipment.estimated_delivery_date,
            "actual_delivery_date": shipment.actual_delivery_date,
            "shipment_boxes": shipment.shipment_boxes,
            "partial_delivery": shipment.partial_delivery,
            "shipment_type": shipment.shipment_type,
        }
        for shipment in shipments
    ]

def parse_invoice_data(invoices):
    """Converts a SQLAlchemy list of objects to a dictionary."""
    
    return [
        {
            "id": invoice.id,
            "customer_name": (f"{invoice.user.first_name} {invoice.user.last_name}"),
            "user_id": invoice.user_id,
            "order_id": invoice.order_id,
            "shipment_id": invoice.shipment_id,
            "total_cost": invoice.total_cost,
            "invoice_date": invoice.invoice_date,
            "due_date": invoice.due_date,
            "overdue": invoice.days_overdue
        }
        for invoice in invoices
    ]

def parse_schedule_data(products):
    """Converts a SQLAlchemy list of objects to a dictionary."""

    return [
        {
            "id": product.id,
            "flavor": product.flavor,
            "container_size": product.container_size,
            "price": product.price,
            "quantity": product.quantity,
            "status": product.status,
            "dock_date": product.dock_date if product.dock_date else None,
        }
        for product in products
    ]
    
def parse_ticket_data(tickets):    
    return [
        {
            "id": ticket.id,
            "source": ticket.source,
            "date_reported": ticket.date_reported,
            "date_detected": ticket.date_detected,
            "date_resolved": ticket.date_resolved,
            "problem_type": ticket.problem_type,
            "problem_description": ticket.problem_description,
            "problem_status": ticket.problem_status,
            "problem_resolution": ticket.problem_resolution
        }
        for ticket in tickets
    ]
