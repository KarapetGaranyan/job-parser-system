from database.models import Vacancy, Session
from utils.search import SearchUtils


class StatsService:
    def get_db_statistics(self):
        """Получение базовой статистики БД"""
        session = Session()
        try:
            total_count = session.query(Vacancy).count()
            hh_count = session.query(Vacancy).filter_by(source='hh').count()
            sj_count = session.query(Vacancy).filter_by(source='superjob').count()

            return {
                'total_vacancies': total_count,
                'hh_vacancies': hh_count,
                'superjob_vacancies': sj_count
            }
        finally:
            session.close()

    def get_full_statistics(self):
        """Получение полной статистики"""
        session = Session()
        try:
            stats = SearchUtils.get_statistics(session)
            return stats
        finally:
            session.close()
