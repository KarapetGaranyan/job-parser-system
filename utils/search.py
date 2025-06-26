from database.models import Vacancy, Session
from sqlalchemy import func
from typing import Dict, List


class SearchUtils:
    """Утилиты для работы с поиском и данными"""

    @staticmethod
    def vacancy_to_dict(vacancy: Vacancy) -> Dict:
        """Конвертация объекта вакансии в словарь"""
        return {
            'id': vacancy.id,
            'title': vacancy.title,
            'link': vacancy.link,
            'company': vacancy.company,
            'salary': vacancy.salary,
            'location': vacancy.location,
            'description': vacancy.description,
            'requirements': vacancy.requirements,
            'source': vacancy.source,
            'created_at': vacancy.created_at.isoformat() if vacancy.created_at else None
        }

    @staticmethod
    def get_statistics(session: Session) -> Dict:
        """Получение статистики по вакансиям"""
        total_count = session.query(Vacancy).count()

        # Статистика по источникам
        source_stats = session.query(
            Vacancy.source,
            func.count(Vacancy.id).label('count')
        ).group_by(Vacancy.source).all()

        # Статистика по компаниям
        company_stats = session.query(
            Vacancy.company,
            func.count(Vacancy.id).label('count')
        ).filter(
            Vacancy.company.isnot(None),
            Vacancy.company != ''
        ).group_by(Vacancy.company).order_by(
            func.count(Vacancy.id).desc()
        ).limit(10).all()

        # Статистика по локациям
        location_stats = session.query(
            Vacancy.location,
            func.count(Vacancy.id).label('count')
        ).filter(
            Vacancy.location.isnot(None),
            Vacancy.location != ''
        ).group_by(Vacancy.location).order_by(
            func.count(Vacancy.id).desc()
        ).limit(10).all()

        return {
            'total_vacancies': total_count,
            'by_source': {item[0]: item[1] for item in source_stats},
            'top_companies': [{'name': item[0], 'count': item[1]} for item in company_stats],
            'top_locations': [{'name': item[0], 'count': item[1]} for item in location_stats]
        }