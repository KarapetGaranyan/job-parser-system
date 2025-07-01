import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import types
# Мокаем StatsService до импорта app_module
import services.stats_service as ss
class DummyStatsService:
    def get_full_statistics(self):
        return {'total': 42}
ss.StatsService = DummyStatsService
import app as app_module

def test_api_stats():
    app = app_module.create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Без авторизации
        resp = client.get('/api/stats')
        assert resp.status_code == 401
        # С авторизацией
        with client.session_transaction() as sess:
            sess['user'] = 'testuser'
        resp2 = client.get('/api/stats')
        data2 = resp2.get_json()
        assert resp2.status_code == 200
        assert data2['success'] is True
        assert data2['stats']['total'] == 42
        print('test_api_stats: OK')

if __name__ == "__main__":
    test_api_stats() 