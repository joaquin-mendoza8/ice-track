from app.extensions import db
from app.models import AdminConfig
from app.utils.checks import check_container_sizes_in_use, check_flavors_in_use, \
                            check_shipping_types_in_use


def update_auto_signoff_interval(request_auto_signoff_interval):
    """
    Update the auto signoff interval in the database with the provided value.
    """
    
    # convert the auto signoff interval to an integer
    request_auto_signoff_interval = int(request_auto_signoff_interval)

    # get the auto signoff interval from the database
    auto_signoff_config = AdminConfig.query.filter_by(key='auto_signoff_interval').first()

    # update the setting in the database, if it exists
    if auto_signoff_config is not None:
        auto_signoff_config.value = request_auto_signoff_interval
    else:
        # create the setting in the database, if it does not exist
        auto_signoff_config = AdminConfig(key='auto_signoff_interval', 
                                            value=request_auto_signoff_interval, 
                                            type='int')
        db.session.add(auto_signoff_config)


def update_supported_container_sizes(request_supported_container_sizes):
    """
    Update the supported container sizes in the database with the provided values.

    Returns an error message if any of the container sizes are in use.
    """

    supported_container_sizes_list = [size.strip().lower() for size in request_supported_container_sizes.split(',')]
    supported_container_sizes_str = ','.join(supported_container_sizes_list)
    supported_container_sizes_config = AdminConfig.query.filter_by(key='supported_container_sizes').first()

    # check if the container sizes are different
    if supported_container_sizes_config:
        # format the database container sizes into a list
        current_container_sizes = supported_container_sizes_config.value.split(',')

        # compare the current container sizes to the ones passed in the request
        if set(current_container_sizes) != set(supported_container_sizes_list):
            container_sizes_in_use = check_container_sizes_in_use(supported_container_sizes_list)

            # if any container sizes are in use, redirect back to the admin dashboard w/ an error message
            if container_sizes_in_use:
                msg = (f"Cannot complete action. Container sizes in use: <{', '.join(container_sizes_in_use)}>. "
                        "Please remove these container sizes from the list before updating.")
                return msg
            
            # else, update the setting in the database
            supported_container_sizes_config.value = supported_container_sizes_str

    # if the setting does not exist, create it
    else:
        container_sizes_config = AdminConfig(key='supported_container_sizes', 
                                                value=supported_container_sizes_str, 
                                                type='list')
        db.session.add(container_sizes_config)


def update_supported_flavors(request_supported_flavors):
    """
    Update the supported flavors in the database with the provided values.

    Returns an error message if any of the flavors are in use.  
    """

    # convert the supported flavors to a list
    supported_flavors_list = [flavor.strip().lower() for flavor in request_supported_flavors.split(',')]
    supported_flavors_str = ','.join(set(supported_flavors_list))
    supported_flavors_config = AdminConfig.query.filter_by(key='supported_flavors').first()

    if supported_flavors_config:
        # format the current database flavors into a list
        current_flavors = supported_flavors_config.value.split(',')

        # set the supported flavors if they are different
        if set(current_flavors) != set(supported_flavors_list):

            flavors_to_remove = set(current_flavors) - set(supported_flavors_list)
            if flavors_to_remove:
                flavors_in_use = check_flavors_in_use(list(flavors_to_remove))
                if flavors_in_use:
                    msg = (f"Cannot complete action. Flavors in use: <{', '.join(flavors_in_use)}>. "
                            "Please remove these flavors from the list before updating.")
                    return msg

        supported_flavors_config.value = supported_flavors_str
    else:
        flavors_config = AdminConfig(key='supported_flavors', 
                                        value=supported_flavors_str, 
                                        type='list')
        db.session.add(flavors_config)


def update_shipping_types(shipping_types_list):
    """
    Update the supported shipping types in the database with the provided values.

    Returns an error message if any of the shipping types are in use.
    """
    supported_shipping_types_str = ','.join(shipping_types_list)
    supported_shipping_types_config = AdminConfig.query.filter_by(key='supported_shipping_types').first()

    if supported_shipping_types_config:
        # format the current database shipping types into a list
        current_shipping_types = supported_shipping_types_config.value.split(',')

        # set the supported shipping types if they are different
        if set(current_shipping_types) != set(shipping_types_list):

            shipping_types_to_update = set(current_shipping_types) - set(shipping_types_list)

            if shipping_types_to_update:
                shipping_types_in_use = check_shipping_types_in_use(list(shipping_types_to_update))
                if shipping_types_in_use:
                    msg = (f"Cannot complete action. Shipping types in use: <{', '.join(shipping_types_in_use)}>. "
                        "Please remove these shipping types from the list before updating.")
                    return msg

            supported_shipping_types_config.value = supported_shipping_types_str
    else:
        shipping_types_config = AdminConfig(key='supported_shipping_types', value=supported_shipping_types_str, type='list')
        db.session.add(shipping_types_config)

def update_shipping_costs(shipping_costs_list):
    """
    Update the supported shipping costs in the database with the provided values.
    """
    try:
        supported_shipping_costs_list = [float(cost) for cost in shipping_costs_list.split(',')]
    except ValueError:
        return "Invalid input: All shipping costs must be valid numbers."
    supported_shipping_costs_str = ','.join([str(cost) for cost in supported_shipping_costs_list])
    supported_shipping_costs_config = AdminConfig.query.filter_by(key='supported_shipping_costs').first()

    if supported_shipping_costs_config:
        supported_shipping_costs_config.value = supported_shipping_costs_str
    else:
        shipping_costs_config = AdminConfig(key='supported_shipping_costs', value=supported_shipping_costs_str, type='list')
        db.session.add(shipping_costs_config)

def update_shipping_data(shipping_types_list, shipping_costs_list):
    """
    Update the supported shipping types and costs in the database with the provided values.

    Returns an error message if any of the shipping types are in use.
    """
    msg = update_shipping_types(shipping_types_list)
    if msg:
        return msg

    msg = update_shipping_costs(shipping_costs_list)
    if msg:
        return msg


def process_pre_delete_container_sizes(config):
    """
    Process the pre-deletion logic of supported container sizes.

    Returns an error message if any of the container sizes are in use.
    """

    # get the supported container sizes from the database
    supported_container_sizes_list = config.value.split(',')

    # get the container sizes that are in use
    container_sizes_in_use = check_container_sizes_in_use(supported_container_sizes_list)

    # if any container sizes are in use, return an error message
    if container_sizes_in_use:
        container_sizes_in_use_str = ', '.join(container_sizes_in_use)
        return (f"Cannot complete action. Container sizes in use: <{container_sizes_in_use_str}>. "
                "Please remove these container sizes from the list before updating.")
    return None


def process_pre_delete_flavors(config):
    """
    Process the pre-deletion logic of supported flavors.

    Returns an error message if any of the flavors are in use.
    """

    # get the supported flavors from the database
    supported_flavors_list = config.value.split(',')

    # get the flavors that are in use
    flavors_in_use = check_flavors_in_use(supported_flavors_list)

    # if any flavors are in use, return an error message
    if flavors_in_use:
        flavors_in_use_str = ', '.join(flavors_in_use)
        return (f"Cannot complete action. Flavors in use: <{flavors_in_use_str}>. "
                "Please remove these flavors from the list before updating.")
    return None