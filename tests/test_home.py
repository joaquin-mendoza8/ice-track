
def test_home_page_get_success(client):
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/inventory'
    assert b'<title>Inventory</title>' in response.data
