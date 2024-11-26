
def extract_order_items(request_form):
    """Extracts order line-item data from a form request."""
    order_items_data = []
    for key in request_form:
        if key.startswith('order_items'):
            index = int(key.split('[')[1].split(']')[0])
            item_key = key.split('[')[2].split(']')[0].replace('-', '_')
            if len(order_items_data) <= index:
                order_items_data.append({})
            value = request_form.get(key)
            if item_key == 'quantity':
                value = int(value)
            elif item_key == 'line_item_cost':
                value = float(value)
            order_items_data[index][item_key] = value

    return order_items_data

def extract_relevant_values(order_item, keys):
    """Extracts relevant values from the order item based on the specified keys."""
    return {key: order_item.get(key) for key in keys}

def compare_order_items(order_item1, order_item2, keys):
    """Compares specific values of two order items for equality."""
    values1 = extract_relevant_values(order_item1, keys)
    values2 = extract_relevant_values(order_item2, keys)
    return values1 == values2