import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import types
# Мокаем SearchService до импорта app_module
import services.search_service as ss
class DummySearchService:
    def search_all_sources(self, query, city='', limit=50):
        return {'query': query, 'vacancies': [{'title': 'Test'}], 'sources': {}, 'total': 1}
ss.SearchService = DummySearchService
import app as app_module

def test_api_search():
    app = app_module.create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Без авторизации
        resp = client.post('/api/search', json={'query': 'python'})
        assert resp.status_code == 401
        # С авторизацией
        with client.session_transaction() as sess:
            sess['user'] = 'testuser'
        resp2 = client.post('/api/search', json={'query': 'python'})
        data2 = resp2.get_json()
        assert resp2.status_code == 200
        assert data2['success'] is True
        assert data2['results']['total'] == 1
        print('test_api_search: OK')

if __name__ == "__main__":
    test_api_search() 