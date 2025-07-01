import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import tempfile
import types
from parsers.base_parser import BaseParser

class DummyParser(BaseParser):
    def search(self, query: str, limit: int = 20, city: str = ''):
        return []

class DummySession:
    def __init__(self, existing=False, fail_commit=False):
        self._existing = existing
        self._fail_commit = fail_commit
        self.added = None
        self.committed = False
        self.rolled_back = False
        self.closed = False
    def query(self, *args, **kwargs):
        class DummyQuery:
            def __init__(self, existing):
                self._existing = existing
            def filter_by(self, **kwargs):
                class DummyFirst:
                    def __init__(self, existing):
                        self._existing = existing
                    def first(self):
                        if self._existing:
                            return object()  # vacancy exists
                        return None
                return DummyFirst(self._existing)
        return DummyQuery(self._existing)
    def add(self, obj):
        self.added = obj
    def commit(self):
        if self._fail_commit:
            raise Exception('DB commit error')
        self.committed = True
    def rollback(self):
        self.rolled_back = True
    def close(self):
        self.closed = True

class DummyVacancy:
    def __init__(self, *args, **kwargs):
        pass

def test_save_vacancy_new():
    parser = DummyParser('test_source')
    vacancy_data = {
        'title': 'Test Vacancy',
        'link': 'http://example.com/vacancy/1',
        'company': 'Test Company',
        'salary': '100000',
    }
    sys.modules['database.models'] = types.SimpleNamespace(
        Vacancy=DummyVacancy,
        Session=lambda: DummySession()
    )
    result = parser.save_vacancy(vacancy_data)
    assert result is True, f"save_vacancy должен вернуть True, а вернул: {result}"

def test_save_vacancy_exists():
    parser = DummyParser('test_source')
    vacancy_data = {
        'title': 'Test Vacancy',
        'link': 'http://example.com/vacancy/1',
        'company': 'Test Company',
        'salary': '100000',
    }
    sys.modules['database.models'] = types.SimpleNamespace(
        Vacancy=DummyVacancy,
        Session=lambda: DummySession(existing=True)
    )
    result = parser.save_vacancy(vacancy_data)
    assert result is False, f"save_vacancy должен вернуть False, если вакансия уже есть, а вернул: {result}"

def test_save_vacancy_commit_error():
    parser = DummyParser('test_source')
    vacancy_data = {
        'title': 'Test Vacancy',
        'link': 'http://example.com/vacancy/1',
        'company': 'Test Company',
        'salary': '100000',
    }
    sys.modules['database.models'] = types.SimpleNamespace(
        Vacancy=DummyVacancy,
        Session=lambda: DummySession(fail_commit=True)
    )
    result = parser.save_vacancy(vacancy_data)
    assert result is False, f"save_vacancy должен вернуть False при ошибке commit, а вернул: {result}"

if __name__ == "__main__":
    test_save_vacancy_new()
    print("test_save_vacancy_new: OK")
    test_save_vacancy_exists()
    print("test_save_vacancy_exists: OK")
    test_save_vacancy_commit_error()
    print("test_save_vacancy_commit_error: OK") 