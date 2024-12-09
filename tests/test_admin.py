import pytest
from app.models import AdminConfig
from app.extensions import db


def test_admin_get(client):
    """Test the admin home page."""

    response = client.get('/admin')
    print(response.data)
    assert response.request.path == '/admin'
    assert response.status_code == 200
    assert b'<title>Admin</title>' in response.data


# NOTE: will fail in CI/CD pipeline since the database is not seeded
@pytest.mark.parametrize('iter', [
    1,
    2,
    3,
    4,
    5
])
def test_admin_config_update(client, app_instance, captured_templates, test_admin_config, iter):
    """Test updating the admin configurations (then revert to originals)."""

    with app_instance.app_context():

        # Prepare data for the post request
        data = {
            'auto-signoff-interval': AdminConfig.query.filter_by(key='auto_signoff_interval').first().value,
            'container-sizes': AdminConfig.query.filter_by(key='supported_container_sizes').first().value,
            'flavors': AdminConfig.query.filter_by(key='supported_flavors').first().value,
            'shipping-types': AdminConfig.query.filter_by(key='supported_shipping_types').first().value if iter != 3 else 'unequal lengths,',
            'shipping-costs': AdminConfig.query.filter_by(key='supported_shipping_costs').first().value if iter != 4 else ''
        }

        # alter the data based on the iteration to cause errors
        if iter == 1:
            data['shipping-types'] = 'standard'
        elif iter == 2:
            data['shipping-costs'] = 'invalid'

        # Update the configuration with a post request
        response = client.post('/admin/update_configs', data=data, follow_redirects=True)

        # Check if the response was successful
        assert response.status_code == 200
        assert response.request.path == '/admin'

        # Check if any messages were passed to the template
        template, context = captured_templates[0]
        assert template.name == 'admin/admin.html'

        # check the message based on the iteration
        if iter == 1:
            assert context.get('msg') == "Shipping types and costs must be equal in length. Please try again."
        elif iter == 2:
            assert context.get('msg') == "Shipping costs must be numbers. Please try again."
        elif iter == 3:
            assert context.get('msg') == "Shipping types cannot be empty. Please try again."
        elif iter == 4:
            assert context.get('msg') == "Missing required fields. Please try again."
        elif iter == 5:
            if context.get('msg_type') == 'danger':
                assert "Cannot complete action." in context.get('msg')
            elif context.get('msg_type') == 'success':
                assert context.get('msg') == "Configuration updated successfully."


def test_admin_delete_config(client, app_instance, captured_templates):
    """Test deleting an admin configuration."""

    with app_instance.app_context():

        # add a dummy configuration to the database
        dummy_config = AdminConfig(key='dummy', value='dummy', type='str')
        db.session.add(dummy_config)
        db.session.commit()

        # Prepare data for the post request
        data = {
            'config-id': dummy_config.id
        }

        # Delete the configuration with a post request
        response = client.post('/admin/delete_config', data=data, follow_redirects=True)

        # Check if the response was successful
        assert response.status_code == 200
        assert response.request.path == '/admin'

        # Check if any messages were passed to the template
        template, context = captured_templates[0]
        assert template.name == 'admin/admin.html'
        assert context.get('msg') == "Configuration deleted successfully." 