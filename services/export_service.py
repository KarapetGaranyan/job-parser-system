from database.models import Vacancy, Session
from utils.export import ExportUtils


class ExportService:
    def export_to_csv(self):
        """Экспорт в CSV"""
        session = Session()
        try:
            vacancies = session.query(Vacancy).all()
            return ExportUtils.to_csv(vacancies)
        finally:
            session.close()

    def export_to_text(self):
        """Экспорт в текст"""
        session = Session()
        try:
            vacancies = session.query(Vacancy).all()
            return ExportUtils.to_text(vacancies)
        finally:
            session.close()