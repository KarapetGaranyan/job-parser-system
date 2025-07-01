import sys
import os
import types
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import parsers.superjob_parser as sj

def test_superjobparser_search():
    # Мокаем requests.get
    class DummyResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {
                'objects': [
                    {
                        'profession': 'Test Vacancy',
                        'link': 'http://test/vacancy',
                        'firm_name': 'Test Company',
                        'payment_from': 1000,
                        'payment_to': 2000,
                        'currency': 'RUB'
                    }
                ],
                'more': False
            }
    def fake_get(url, headers=None, params=None, timeout=None):
        return DummyResponse()
    sj.requests.get = fake_get

    # Мокаем save_vacancy чтобы не писать в БД
    class DummyBase(sj.BaseParser):
        def search(self, *a, **k):
            return []
        def save_vacancy(self, vacancy_data):
            return True
    sj.SuperJobParser.__bases__ = (DummyBase,)

    parser = sj.SuperJobParser()
    result = parser.search('python', limit=1)
    assert len(result) == 1
    assert result[0]['title'] == 'Test Vacancy'
    assert result[0]['salary'] == 'от 1000 до 2000 RUB'
    print('test_superjobparser_search: OK')

if __name__ == "__main__":
    test_superjobparser_search() 