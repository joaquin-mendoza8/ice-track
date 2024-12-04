from app.extensions import db
from app.models import AdminConfig

def fetch_autosignoff_interval():
    """
    Function to fetch the auto signoff interval from the database.
    Defaults to 60 (minutes) if the setting does not exist.
    """

    # set the default interval to 60 minutes
    default_interval = 60

    # get the auto signoff interval from the database
    auto_signoff_config = AdminConfig.query.filter_by(key='auto_signoff_interval').first()

    # return the auto signoff interval, or 
    return auto_signoff_config.value if auto_signoff_config else default_interval

def fetch_supported_container_sizes():
    """
    Function to fetch the supported container sizes from the database.
    Defaults to ['small', 'medium', 'large'] if the setting does not exist.
    """

    # set the default container sizes
    default_container_sizes = ['small', 'medium', 'large']

    # get the supported container sizes from the database
    container_sizes_config = AdminConfig.query.filter_by(key='supported_container_sizes').first()

    # format the container sizes as a list
    container_sizes_config = container_sizes_config.value.split(',') if container_sizes_config else None

    # return the supported container sizes, or the default
    return container_sizes_config if container_sizes_config else default_container_sizes

def fetch_supported_flavors():
    """
    Function to fetch the supported flavors from the database.
    Defaults to ['chocolate', 'vanilla', 'strawberry'] if the setting does not exist.
    """

    # set the default flavors
    default_flavors = ['chocolate', 'vanilla', 'strawberry']

    # get the supported flavors from the database
    supported_flavors_config = AdminConfig.query.filter_by(key='supported_flavors').first()

    # format the flavors as a list
    supported_flavors_config = supported_flavors_config.value.split(',') if supported_flavors_config else None

    # return the supported flavors, or the default
    return supported_flavors_config if supported_flavors_config else default_flavors