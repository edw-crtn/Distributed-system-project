import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

def test_root_route():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hello' in response.data

def test_test_route():
    client = app.test_client()
    response = client.get('/test')
    assert response.status_code == 200
    assert b'Test' in response.data
