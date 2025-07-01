import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app as app_module

def test_main_index_auth():
    app = app_module.create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Без авторизации — должен быть редирект на login
        resp = client.get('/', follow_redirects=False)
        assert resp.status_code in (301, 302)
        assert '/auth/login' in resp.headers['Location']
        # С авторизацией — должен быть 200 и index.html
        with client.session_transaction() as sess:
            sess['user'] = 'testuser'
        resp2 = client.get('/')
        assert resp2.status_code == 200
        assert b'<form' in resp2.data
        print('test_main_index_auth: OK')

if __name__ == "__main__":
    test_main_index_auth() 