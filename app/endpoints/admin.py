from flask import Blueprint, render_template, request, redirect, url_for
from app.utils.admin_decorator import admin_required
from app.extensions import db
from app.models import AdminConfig, Product
from app.utils.checks import check_container_sizes_in_use, check_flavors_in_use
from app.utils.data import parse_admin_config_data

# create the admin blueprint
admin = Blueprint('admin', __name__)


# ROUTES

# admin home endpoint
@admin.route('/admin')
@admin_required
def admin_home():

    # fetch all admin configurations from the database
    configs = AdminConfig.query.all()

    # parse the admin configuration data into a dictionary
    formatted_configs = parse_admin_config_data(configs)

    # get individual configuration objects from list of configurations
    auto_signoff_interval, supported_container_sizes, supported_flavors = None, None, None
    for config in configs:
        if config.key == 'auto_signoff_interval':
            auto_signoff_interval = config.value
        elif config.key == 'supported_container_sizes':
            supported_container_sizes = config.value
        elif config.key == 'supported_flavors':
            supported_flavors = config.value

    # dictionary of items to pass to the template
    jinja_vars = {
        'configs': formatted_configs,
        'auto_signoff_interval': auto_signoff_interval,
        'supported_container_sizes': supported_container_sizes,
        'supported_flavors': supported_flavors,
    }

    # fetch any messages passed to the template
    msg = request.args.get('msg')

    # print(f"Message: {msg}")

    # if a message was passed, add it to the dictionary
    if msg:
        jinja_vars['msg'] = str(msg)

    return render_template('admin/admin.html', **jinja_vars)

# admin update configuration endpoint
@admin.route('/admin/update_configs', methods=['POST'])
def update_admin_config():

    # get the request form data
    request_auto_signoff_interval = request.form.get('auto-signoff-interval')
    supported_container_sizes = request.form.get('container-sizes')
    supported_flavors = request.form.get('flavors')

    # if none of the fields were passed, redirect back to the admin dashboard
    if not all([request_auto_signoff_interval, supported_container_sizes, supported_flavors]):
        return redirect(url_for('admin.admin_home'))

    # update the auto signoff interval, if it was passed
    if request_auto_signoff_interval:

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

    # update the supported container sizes, if it was passed
    if supported_container_sizes:
        supported_container_sizes_list = [size.strip().lower() for size in supported_container_sizes.split(',')]
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
                    container_sizes_in_use_str = ', '.join(container_sizes_in_use)
                    msg = (f"Cannot complete action. Container sizes in use: <{container_sizes_in_use_str}>. "
                           "Please remove these container sizes from the list before updating.")
                    return redirect(url_for('admin.admin_home', msg=msg))
                
                # else, update the setting in the database
                supported_container_sizes_config.value = supported_container_sizes_str

        # if the setting does not exist, create it
        else:
            container_sizes_config = AdminConfig(key='supported_container_sizes', 
                                                 value=supported_container_sizes_str, 
                                                 type='list')
            db.session.add(container_sizes_config)

    # update the supported flavors, if it was passed
    if supported_flavors:

        # convert the supported flavors to a list
        supported_flavors_list = [flavor.strip().lower() for flavor in supported_flavors.split(',')]
        supported_flavors_str = ','.join(set(supported_flavors_list))
        supported_flavors_config = AdminConfig.query.filter_by(key='supported_flavors').first()

        if supported_flavors_config:
            # format the current database flavors into a list
            current_flavors = supported_flavors_config.value.split(',')

            # set the supported flavors if they are different
            if set(current_flavors) != set(supported_flavors_list):
                # flavors_in_use = check_flavors_in_use(supported_flavors_list)

                flavors_to_remove = set(current_flavors) - set(supported_flavors_list)
                if flavors_to_remove:
                    flavors_in_use = check_flavors_in_use(list(flavors_to_remove))
                    if flavors_in_use:
                        flavors_in_use_str = ', '.join(flavors_in_use)
                        msg = (f"Cannot complete action. Flavors in use: <{flavors_in_use_str}>. "
                               "Please remove these flavors from the list before updating.")
                        return redirect(url_for('admin.admin_home', msg=msg))
                    
            supported_flavors_config.value = supported_flavors_str
        else:
            flavors_config = AdminConfig(key='supported_flavors', 
                                         value=supported_flavors_str, 
                                         type='list')
            db.session.add(flavors_config)

    # commit the changes, if any
    if db.session.dirty:
        db.session.commit()

    return redirect(url_for('admin.admin_home'))
    

# admin delete configuration endpoint
@admin.route('/admin/delete_config', methods=['POST'])
def delete_admin_config():

    # get the request form data
    config_id = request.form.get('config-id')

    # delete the admin configuration from the database
    config = AdminConfig.query.get(config_id)
    if config:

        # check if the configuration is container sizes and if any are in use
        if config.key == 'supported_container_sizes':

            # get the supported container sizes from the database
            supported_container_sizes_list = config.value.split(',')

            # get the supported container sizes from the database
            container_sizes_in_use = check_container_sizes_in_use(supported_container_sizes_list)

            # if any container sizes are in use, redirect back to the admin dashboard with an error message
            if container_sizes_in_use:
                container_sizes_in_use_str = ', '.join(container_sizes_in_use)
                msg = (f"Cannot complete action. Container sizes in use: <{container_sizes_in_use_str}>. "
                       "Please remove these container sizes from the list before updating.")
                return redirect(url_for('admin.admin_home', msg=msg))
            
        # check if the configuration is flavors and if any are in use
        elif config.key == 'supported_flavors':

            # get the supported flavors from the database
            supported_flavors_list = config.value.split(',')

            # get the flavors that are in use
            flavors_in_use = check_flavors_in_use(supported_flavors_list)

            # if any flavors are in use, redirect back to the admin dashboard with an error message
            if flavors_in_use:
                flavors_in_use_str = ', '.join(flavors_in_use)
                msg = (f"Cannot complete action. Flavors in use: <{flavors_in_use_str}>. "
                       "Please remove these flavors from the list before updating.")
                return redirect(url_for('admin.admin_home', msg=msg))

        db.session.delete(config)
        db.session.commit()

        # print a success message
        print(f"Config deleted: {config}")
    else:

        # TODO: log the error / handle the error
        print(f"Config not found: {config}")

    return redirect(url_for('admin.admin_home'))

# TODO: add admin functionalities (e.g. user management, 
#                                       order limits, 
#                                       user-defined lists, 
#                                       etc.)