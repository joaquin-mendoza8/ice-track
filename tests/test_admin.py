import pytest
from app.models import AdminConfig
from app.extensions import db

@pytest.fixture
def admin_configs_orig():
    """Fixture to store the original values of the admin configurations."""

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
    """Test the admin home page."""

    response = client.get('/admin')
    print(response.data)
    assert response.request.path == '/admin'
    assert response.status_code == 200
    assert b'<title>Admin</title>' in response.data

@pytest.mark.skip(reason="Requires a seeded database.")
@pytest.mark.parametrize("config_key, new_value", [
    ('auto_signoff_interval', 10),
    ('supported_container_sizes', 'small,medium,large'),
    ('supported_flavors', 'vanilla,chocolate,strawberry'),
    ('supported_shipping_types', 'standard,express'),
    ('supported_shipping_costs', '5.00,10.00')
])
def test_admin_config_update(client, app_instance, captured_templates, admin_configs_orig, config_key, new_value):
    """Test updating the admin configurations (then revert to originals)."""

    with app_instance.app_context():

        # get a snapshot of the current configuration
        original_config = admin_configs_orig[config_key]

        # Prepare data for the post request
        data = {
            'auto-signoff-interval': admin_configs_orig['auto_signoff_interval'],
            'container-sizes': admin_configs_orig['supported_container_sizes'],
            'flavors': admin_configs_orig['supported_flavors'],
            'shipping-types': admin_configs_orig['supported_shipping_types'],
            'shipping-costs': admin_configs_orig['supported_shipping_costs']
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
        if current_config is not None:
            if current_config.type == 'int':
                assert int(current_config.value) == new_value
            elif current_config.type == 'list':
                assert current_config.value.split(',').sort() == new_value.split(',').sort()
            else:
                assert current_config.value == new_value

        # Revert the changes
        current_config.value = original_config
        db.session.commit()

@pytest.mark.skip(reason="Requires a seeded database.")
@pytest.mark.parametrize("config_key", [
    'auto_signoff_interval',
    'supported_container_sizes',
    'supported_flavors',
    'supported_shipping_types'  # 'supported_shipping_costs' is not included since it is dependent on 'supported_shipping_types'
])
def test_delete_admin_config(client, app_instance, captured_templates, admin_configs_orig, config_key):
    """
    Test deleting admin configurations (then recreate them if applicable).
    
    NOTE: This test should fail if any configuration's value(s) is/are currently being
    used in the application (e.g. supported flavors, shipping types, etc.)."""

    with app_instance.app_context():
        
        # get a snapshot of the current configuration
        current_config = AdminConfig.query.filter_by(key=config_key).first()
        assert current_config is not None
        print(current_config)

        config_id = current_config.id

        # Update the configuration with a post request
        response = client.post('/admin/delete_config', data={'config-id': config_id}, follow_redirects=True)

        # Check if any messages were passed to the template
        template, context = captured_templates[0]

        # the configuration is being used in the application
        if context.get('msg') and context.get('msg_type') != 'success':

            assert "Cannot complete action" in context.get('msg')

        else:

            # the configuration is not being used in the application
            assert response.status_code == 200
            assert response.request.path == '/admin'
            assert template.name == 'admin/admin.html'
            assert context.get('msg_type') != 'danger'

            # Check if the configuration was deleted from the database
            current_config = AdminConfig.query.filter_by(key=config_key).first()
            assert current_config is None

            # Revert the changes (recreate the configuration)
            # original_config = admin_configs_orig[config_key]
            # existing_config = AdminConfig.query.filter_by(key=config_key).first()
            # if existing_config is None:
            #     new_config = AdminConfig(key=config_key, value=original_config, type='int')
            #     db.session.add(new_config)
            #     db.session.commit()
            #     assert new_config.id is not None