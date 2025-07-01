import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.export import ExportUtils

class DummyVacancy:
    def __init__(self, id, title, company, salary, source, link, created_at=None):
        self.id = id
        self.title = title
        self.company = company
        self.salary = salary
        self.source = source
        self.link = link
        self.created_at = created_at

def test_export_to_csv():
    vacancies = [
        DummyVacancy(1, 'Dev', 'Comp', '1000', 'hh', 'http://link', None),
        DummyVacancy(2, 'QA', 'Test', '2000', 'superjob', 'http://link2', None)
    ]
    csv_data = ExportUtils.to_csv(vacancies)
    assert 'Dev' in csv_data and 'QA' in csv_data and 'Название' in csv_data
    print('test_export_to_csv: OK')

def test_export_to_text():
    vacancies = [
        DummyVacancy(1, 'Dev', 'Comp', '1000', 'hh', 'http://link', None),
        DummyVacancy(2, 'QA', 'Test', '2000', 'superjob', 'http://link2', None)
    ]
    text_data = ExportUtils.to_text(vacancies)
    assert 'СПИСОК ВАКАНСИЙ' in text_data and 'Dev' in text_data and 'QA' in text_data
    print('test_export_to_text: OK')

if __name__ == "__main__":
    test_export_to_csv()
    test_export_to_text() 