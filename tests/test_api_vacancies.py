import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import types
# Мокаем VacancyService до импорта app_module
import services.vacancy_service as vs
class DummyVacancyService:
    def get_vacancies_paginated(self, page=1, per_page=10, source='', company=''):
        return {'vacancies': [{'title': 'Test'}], 'total': 1}
vs.VacancyService = DummyVacancyService
import app as app_module

def test_api_vacancies():
    app = app_module.create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Без авторизации
        resp = client.get('/api/vacancies')
        assert resp.status_code == 401
        # С авторизацией
        with client.session_transaction() as sess:
            sess['user'] = 'testuser'
        resp2 = client.get('/api/vacancies')
        data2 = resp2.get_json()
        assert resp2.status_code == 200
        assert data2['success'] is True
        assert data2['data']['total'] == 1
        print('test_api_vacancies: OK')

if __name__ == "__main__":
    test_api_vacancies() 