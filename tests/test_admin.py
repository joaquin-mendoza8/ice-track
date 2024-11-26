import pytest
from app.models import AdminConfig
from app.extensions import db

@pytest.fixture
def admin_configs():
    # Setup: get all admin configurations from the database
    auto_signoff_config = AdminConfig.query.filter_by(key='auto_signoff_interval').first()
    supported_container_sizes_config = AdminConfig.query.filter_by(key='supported_container_sizes').first()
    supported_flavors_config = AdminConfig.query.filter_by(key='supported_flavors').first()
    supported_shipping_types_config = AdminConfig.query.filter_by(key='supported_shipping_types').first()
    supported_shipping_costs_config = AdminConfig.query.filter_by(key='supported_shipping_costs').first()

    # Store the current values of the configurations
    configs = {
        'auto_signoff_interval': auto_signoff_config.value if auto_signoff_config else None,
        'supported_container_sizes': supported_container_sizes_config.value if supported_container_sizes_config else None,
        'supported_flavors': supported_flavors_config.value if supported_flavors_config else None,
        'supported_shipping_types': supported_shipping_types_config.value if supported_shipping_types_config else None,
        'supported_shipping_costs': supported_shipping_costs_config.value if supported_shipping_costs_config else None,
    }

    yield configs


def test_admin_get(client):
    response = client.get('/admin')
    print(response.data)
    assert response.status_code == 200
    assert response.request.path == '/admin'
    assert b'<title>Admin</title>' in response.data

@pytest.mark.skip(reason="Needs to be fixed")
@pytest.mark.parametrize("config_key, new_value", [
    ('auto_signoff_interval', 10),
    ('supported_container_sizes', 'small,medium,large'),
    ('supported_flavors', 'vanilla,chocolate,strawberry'),
    ('supported_shipping_types', 'standard,express'),
    ('supported_shipping_costs', '5.00,10.00')
])
def test_admin_config_update(client, app_instance, captured_templates, admin_configs, config_key, new_value):
    print(admin_configs)
    # assert admin_configs['auto_signoff_interval'] == 60
    with app_instance.app_context():
        # Ensure the configuration exists
        # config = AdminConfig.query.filter_by(key=config_key).first()
        # if not config:
        #     config = AdminConfig(key=config_key, value='')
        #     db.session.add(config)
        #     db.session.commit()

        # get a snapshot of the current configuration
        original_config = AdminConfig.query.filter_by(key=config_key).first().value

        # Prepare data for the post request
        data = {
            'auto-signoff-interval': admin_configs['auto_signoff_interval'],
            'container-sizes': admin_configs['supported_container_sizes'],
            'flavors': admin_configs['supported_flavors'],
            'shipping-types': admin_configs['supported_shipping_types'],
            'shipping-costs': admin_configs['supported_shipping_costs']
        }
        data[config_key.replace('_', '-')] = new_value

        # Update the configuration with a post request
        response = client.post('/admin/update_configs', data=data, follow_redirects=True)

        # Check if the response was successful
        assert response.status_code == 200
        assert response.request.path == '/admin'

        # Check if any messages were passed to the template
        template, context = captured_templates[0]
        assert template.name == 'admin/admin.html'
        assert context.get('msg_type') != 'danger'

        # Check if the configuration was updated
        current_config = AdminConfig.query.filter_by(key=config_key).first()
        if current_config.type == 'int':
            assert int(current_config.value) == new_value
        elif current_config.type == 'list':
            assert current_config.value.split(',').sort() == new_value.split(',').sort()
        else:
            assert current_config.value == new_value

        # Revert the changes
        current_config.value = original_config
        db.session.commit()