import usaddress

# Custom Jinja filters to format data in templates
# NOTE: must name functions with "format_" prefix to be registered as Jinja filters

def format_currency(value):
    """Format value as currency."""
    return "${:,.2f}".format(value)

def format_currency_list(value):
    """Format comma-separated list of strings as currency."""
    return ",".join(format_currency(float(v)) for v in value.split(","))

def format_date(value):
    """Format date as <Mon DD, YYYY>."""
    return value.strftime("%b %d, %Y").replace(" 0", " ")

def format_datetime(value):
    """Format datetime as <Mon DD, YYYY HH:MM>."""
    return value.strftime("%b %d, %Y %H:%M").replace(" 0", " ")

def format_attribute(value):
    """Format SQL attribute as space-delimited titled phrase."""
    return value.replace("_", " ").title()

def format_address(value):
    """Format address using usaddress library."""
    parsed, labels = usaddress.tag(value)

    # labels to title
    title = ['StreetName', 'PlaceName']

    # label to uppercase
    uppercase = 'StateName'

    # perform the formatting
    for label in labels:
        if label in title:
            parsed[label] = parsed[label].title()
        elif label == uppercase:
            parsed[label] = parsed[label].upper()

    # rejoin the parts
    return " ".join(parsed.values())
