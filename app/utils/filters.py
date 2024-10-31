# Custom Jinja filters to format data in templates
# NOTE: must name functions with "format_" prefix to be registered as Jinja filters

def format_currency(value):
    """Format value as currency."""
    return "${:,.2f}".format(value)

def format_date(value):
    """Format date as <Mon DD, YYYY>."""
    return value.strftime("%b %d, %Y").replace(" 0", " ")

def format_attribute(value):
    """Format SQL attribute as space-delimited capitalized phrase."""
    return value.replace("_", " ").capitalize()