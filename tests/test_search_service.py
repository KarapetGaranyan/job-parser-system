import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.search_service import SearchService

class DummyParser:
    def search(self, query, limit=20, city=''):
        return [{'title': 'Test', 'link': 'l', 'company': 'C', 'salary': 'S'}]

def test_search_all_sources():
    service = SearchService()
    service.hh_parser = DummyParser()
    service.sj_parser = DummyParser()
    result = service.search_all_sources('python')
    assert 'vacancies' in result and 'sources' in result and result['total'] == 2
    assert result['sources']['hh']['count'] == 1
    assert result['sources']['superjob']['count'] == 1
    print('test_search_all_sources: OK')

if __name__ == "__main__":
    test_search_all_sources() 