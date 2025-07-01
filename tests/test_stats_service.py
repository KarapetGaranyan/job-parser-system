import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import types

class DummySession:
    def __init__(self):
        self.calls = []
    def query(self, model):
        class DummyQuery:
            def __init__(self, model, calls):
                self.model = model
                self.calls = calls
            def count(self):
                if self.model == 'Vacancy':
                    self.calls.append('count')
                    return 10
                return 0
            def filter_by(self, **kwargs):
                class DummyFilter:
                    def count(self):
                        if kwargs.get('source') == 'hh':
                            return 4
                        if kwargs.get('source') == 'superjob':
                            return 6
                        return 0
                return DummyFilter()
        return DummyQuery(model, self.calls)
    def close(self):
        pass

def test_get_db_statistics():
    sys.modules['database.models'] = types.SimpleNamespace(
        Vacancy='Vacancy',
        Session=lambda: DummySession()
    )
    from services.stats_service import StatsService
    service = StatsService()
    stats = service.get_db_statistics()
    assert stats['total_vacancies'] == 10
    assert stats['hh_vacancies'] == 4
    assert stats['superjob_vacancies'] == 6
    print('test_get_db_statistics: OK')

if __name__ == "__main__":
    test_get_db_statistics() 