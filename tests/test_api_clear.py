import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import types
# Мокаем VacancyService до импорта app_module
import services.vacancy_service as vs
class DummyVacancyService:
    def clear_all_vacancies(self):
        return {'message': 'Cleared', 'deleted_count': 5}
vs.VacancyService = DummyVacancyService
import app as app_module

def test_api_clear():
    app = app_module.create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Без авторизации
        resp = client.post('/api/clear')
        assert resp.status_code == 401
        # С авторизацией, но не admin
        with client.session_transaction() as sess:
            sess['user'] = 'testuser'
            sess['role'] = 'user'
        resp2 = client.post('/api/clear')
        assert resp2.status_code == 403
        # С авторизацией и admin
        with client.session_transaction() as sess:
            sess['user'] = 'admin'
            sess['role'] = 'admin'
        resp3 = client.post('/api/clear')
        data3 = resp3.get_json()
        assert resp3.status_code == 200
        assert data3['success'] is True
        assert data3['deleted_count'] == 5
        print('test_api_clear: OK')

if __name__ == "__main__":
    test_api_clear() 