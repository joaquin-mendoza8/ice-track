import pytest
from dotenv import load_dotenv

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import app

load_dotenv()


def test_login():
    app.testing = True
    client = app.test_client()

    response = client.post('/login', data=dict(username='test', password='test'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid credentials provided.' in response.data

def test_home_page():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 302 or response.status_code == 200
