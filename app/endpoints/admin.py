from flask import Blueprint, render_template, request, redirect, url_for
from app.utils.admin_decorator import admin_required
from app.extensions import db
from app.models import AdminConfig, User
from app.utils.admin_configs import update_auto_signoff_interval, update_supported_container_sizes, \
                                    update_supported_flavors, update_shipping_data, \
                                    process_pre_delete_container_sizes, process_pre_delete_flavors, \
                                    process_pre_delete_shipping_types
from app.utils.data import parse_admin_config_data, parse_customer_data

# create the admin blueprint
admin = Blueprint('admin', __name__)


# ROUTES

# admin home endpoint
@admin.route('/admin')
@admin_required
def admin_home():

    try:

        # fetch all users from the database
        users = User.query.filter_by(is_admin=False).all()

        # parse the users data into a list of dictionaries
        users = parse_customer_data(users)

        # fetch all admin configurations from the database
        configs = AdminConfig.query.all()

        # parse the admin configuration data into a dictionary
        formatted_configs = parse_admin_config_data(configs)

        # get individual configuration objects from list of configurations
        config_map = {
            'auto_signoff_interval': None,
            'supported_container_sizes': None,
            'supported_flavors': None,
            'supported_shipping_types': None,
            'supported_shipping_costs': None
        }
        
        # map the configuration objects to their respective keys
        for config in configs:
            if config.key in config_map:
                config_map[config.key] = config.value

        # format the supported shipping types and costs into key-value pairs
        if config_map['supported_shipping_types'] and config_map['supported_shipping_costs']:
            shipping_types = config_map['supported_shipping_types'].split(',')
            shipping_costs = config_map['supported_shipping_costs'].split(',')
            
            configs.append({
                'key': 'supported_shipping_data',
                'value': dict(zip(shipping_types, shipping_costs))
            })

        # dictionary of items to pass to the template
        jinja_vars = {
            'configs': formatted_configs,
            'users': users,
            **config_map
        }

        # if a message was passed, add it to the dictionary
        msg = request.args.get('msg')
        if msg:
            jinja_vars['msg'] = str(msg)

        # if a message type was passed, add it to the dictionary
        msg_type = request.args.get('msg_type')
        if msg_type:
            jinja_vars['msg_type'] = str(msg_type)

    except Exception as e:
        # log the error
        print(f"Error fetching admin data: {e}")
        jinja_vars = {
            'msg': "An error occurred. Please contact support."
        }

    return render_template('admin/admin.html', **jinja_vars)

# admin update configuration endpoint
@admin.route('/admin/update_configs', methods=['POST'])
def update_admin_config():

    try:

        # get the request form data
        request_auto_signoff_interval = request.form.get('auto-signoff-interval')
        request_supported_container_sizes = request.form.get('container-sizes')
        request_supported_flavors = request.form.get('flavors')
        request_supported_shipping_types = request.form.get('shipping-types')
        request_supported_shipping_costs = request.form.get('shipping-costs')
        request_user_to_elevate = request.form.get('user-select')

        # if there are missing required fields, redirect back to the admin dashboard
        if not all([request_auto_signoff_interval, request_supported_container_sizes, 
                    request_supported_flavors, request_supported_shipping_types,
                    request_supported_shipping_costs]):
            msg = "Missing required fields. Please try again."
            return redirect(url_for('admin.admin_home', msg=msg))
        
        # deduplication and input-validation for shipping types and costs
        shipping_types_list = []
        for shipping_type in request_supported_shipping_types.strip().split(','):
            if not shipping_type.strip(): # redirect if shipping type is empty
                msg = "Shipping types cannot be empty. Please try again."
                return redirect(url_for('admin.admin_home', msg=msg))
            if shipping_type.strip().lower() not in shipping_types_list:
                shipping_types_list.append(shipping_type.strip())
        shipping_costs_list = []
        for shipping_cost in request_supported_shipping_costs.strip().split(','):
            try: # redirect if shipping cost is not a number
                round(float(shipping_cost.strip()), 2)
                shipping_costs_list.append(shipping_cost)
            except ValueError:
                msg = "Shipping costs must be numbers. Please try again."
                return redirect(url_for('admin.admin_home', msg=msg))

        # if the length of the supported shipping types and costs are not equal, redirect back to the admin dashboard
        if len(shipping_types_list) != len(shipping_costs_list):
            msg = "Shipping types and costs must be equal in length. Please try again."
            return redirect(url_for('admin.admin_home', msg=msg))

        # update the auto signoff interval, if it was passed
        if request_auto_signoff_interval:
            update_auto_signoff_interval(request_auto_signoff_interval)

        # update the supported container sizes, if it was passed
        if request_supported_container_sizes:
            msg = update_supported_container_sizes(request_supported_container_sizes)

            # if an error message was returned, redirect back to the admin dashboard with the error message
            if msg:
                return redirect(url_for('admin.admin_home', msg=msg))

        # update the supported flavors, if it was passed
        if request_supported_flavors:
            msg = update_supported_flavors(request_supported_flavors)

            # if an error message was returned, redirect back to the admin dashboard with the error message
            if msg:
                return redirect(url_for('admin.admin_home', msg=msg))
            
        # update the supported shipping types/cost if passed
        if shipping_types_list and request_supported_shipping_costs:
            msg = update_shipping_data(shipping_types_list, request_supported_shipping_costs)

            # if an error message was returned, redirect back to the admin dashboard with the error message
            if msg:
                return redirect(url_for('admin.admin_home', msg=msg))
            
        # update the user to an admin, if a user was selected
        if request_user_to_elevate:
            user = User.query.get(request_user_to_elevate)
            if user:
                user.is_admin = True
            else:
                msg = "User not found. Please try again."
                return redirect(url_for('admin.admin_home', msg=msg))

        # commit the changes, if any
        if db.session.dirty:
            msg = "Configuration updated successfully."
            msg_type = "success"
            db.session.commit()

    except Exception as e:
        # log the error
        print(f"Error updating configuration: {e}")
        msg = "An error occurred. Please contact support."
        db.session.rollback()

    return redirect(url_for('admin.admin_home', msg=msg, msg_type=msg_type))
    

# admin delete configuration endpoint
@admin.route('/admin/delete_config', methods=['POST'])
def delete_admin_config():

    try:

        # get the request form data
        config_id = request.form.get('config-id')

        # delete the admin configuration from the database
        config = AdminConfig.query.get(config_id)
        if config:

            # dictionary to map config keys to their respective pre-delete processing functions
            pre_delete_functions = {
                'supported_container_sizes': process_pre_delete_container_sizes,
                'supported_flavors': process_pre_delete_flavors,
                'supported_shipping_types': process_pre_delete_shipping_types,
            }

            # call the appropriate pre-delete function if the config key exists in the dictionary
            if config.key in pre_delete_functions:
                msg = pre_delete_functions[config.key](config)

                # if an error message was returned, redirect back to the admin dashboard with the error message
                if msg:
                    return redirect(url_for('admin.admin_home', msg=msg))

            # delete the configuration from the database
            db.session.delete(config)
            db.session.commit()

            # print a success message
            print(f"Config deleted: {config}")
            msg = "Configuration deleted successfully."
            msg_type = "success"

        else:
            # print an error message
            print(f"Config not found: {config}")
            msg = "Configuration not found. Please try again."

    except Exception as e:
        # log the error
        print(f"Error deleting configuration: {e}")
        msg = "An error occurred. Please contact support."
        db.session.rollback()

    return redirect(url_for('admin.admin_home', msg=msg, msg_type=msg_type))
