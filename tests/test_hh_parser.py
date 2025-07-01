import sys
import os
import types
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import parsers.hh_parser as hh

def test_hhparser_search():
    # Мокаем requests.get
    class DummyResponse:
        def __init__(self, text):
            self.text = text
        def raise_for_status(self):
            pass
    def fake_get(url, headers=None, params=None, timeout=None):
        return DummyResponse('<html></html>')
    hh.requests.get = fake_get

    # Мокаем BeautifulSoup
    class DummySoup:
        def __init__(self, text, parser):
            pass
        def find_all(self, tag, attrs=None):
            class DummyItem:
                def find(self, tag, attrs=None, class_=None):
                    class DummyTag:
                        text = 'Test Vacancy'
                        def __getitem__(self, key):
                            return 'http://test/vacancy'
                    if tag == 'a' and (attrs and attrs.get('data-qa') == 'serp-item__title'):
                        return DummyTag()
                    if tag == 'a' and (attrs and attrs.get('data-qa') == 'vacancy-serp__vacancy-employer'):
                        return DummyTag()
                    if tag == 'span' and (attrs and attrs.get('data-qa') == 'vacancy-serp__vacancy-compensation'):
                        return DummyTag()
                    return None
            return [DummyItem()]
    hh.BeautifulSoup = DummySoup

    # Мокаем save_vacancy чтобы не писать в БД
    class DummyBase(hh.BaseParser):
        def search(self, *a, **k):
            return []
        def save_vacancy(self, vacancy_data):
            return True
    hh.HHParser.__bases__ = (DummyBase,)

    parser = hh.HHParser()
    result = parser.search('python', limit=1)
    assert len(result) == 1
    assert result[0]['title'] == 'Test Vacancy'
    print('test_hhparser_search: OK')

if __name__ == "__main__":
    test_hhparser_search() 