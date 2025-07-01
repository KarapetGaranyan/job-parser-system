import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app as app_module
import pytest

def test_api_health():
    app = app_module.create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Без авторизации
        resp = client.get('/api/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'
        assert data['authenticated'] is False
        # С авторизацией
        with client.session_transaction() as sess:
            sess['user'] = 'testuser'
        resp2 = client.get('/api/health')
        data2 = resp2.get_json()
        assert data2['authenticated'] is True
        assert data2['user'] == 'testuser'
        print('test_api_health: OK')

if __name__ == "__main__":
    test_api_health() 