import sys
import os
import types
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.search import SearchUtils

def test_vacancy_to_dict():
    class DummyVacancy:
        def __init__(self):
            self.id = 1
            self.title = 'Dev'
            self.link = 'l'
            self.company = 'C'
            self.salary = '1000'
            self.location = 'Moscow'
            self.description = 'desc'
            self.requirements = 'req'
            self.source = 'hh'
            self.created_at = datetime(2024, 1, 1, 12, 0)
    v = DummyVacancy()
    d = SearchUtils.vacancy_to_dict(v)
    assert d['title'] == 'Dev' and d['location'] == 'Moscow' and d['created_at'].startswith('2024-01-01')
    print('test_vacancy_to_dict: OK')

def test_get_statistics():
    class DummyIsNot:
        def isnot(self, val):
            return self
        def __ne__(self, other):
            return self
    class DummyVacancy:
        id = 1
        source = 'hh'
        company = DummyIsNot()
        location = DummyIsNot()
    class DummySession:
        def query(self, *args, **kwargs):
            class DummyQuery:
                def count(self):
                    return 5
                def group_by(self, *args, **kwargs):
                    return self
                def all(self):
                    # Мокаем возврат для разных запросов
                    if args and hasattr(args[0], 'source'):
                        return [('hh', 3), ('superjob', 2)]
                    if args and hasattr(args[0], 'company'):
                        return [('C1', 2), ('C2', 1)]
                    if args and hasattr(args[0], 'location'):
                        return [('Moscow', 3), ('SPB', 2)]
                    return []
                def filter(self, *args, **kwargs):
                    return self
                def filter_by(self, **kwargs):
                    return self
                def order_by(self, *args, **kwargs):
                    return self
                def limit(self, n):
                    return self
            return DummyQuery()
    class DummyCount:
        def label(self, name):
            return self
        def desc(self):
            return self
    import utils.search as us
    us.func = types.SimpleNamespace(count=lambda x: DummyCount())
    us.Vacancy = DummyVacancy
    stats = SearchUtils.get_statistics(DummySession())
    assert stats['total_vacancies'] == 5
    print('test_get_statistics: OK')

if __name__ == "__main__":
    test_vacancy_to_dict()
    test_get_statistics() 