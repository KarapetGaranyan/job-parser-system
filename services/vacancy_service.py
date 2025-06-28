from database.models import Vacancy, Session
from sqlalchemy import or_
from utils.search import SearchUtils


class VacancyService:
    def get_vacancies_paginated(self, page=1, per_page=10, source='', company=''):
        """Получение вакансий с пагинацией и фильтрами"""
        session = Session()
        try:
            query = session.query(Vacancy)

            # Применяем фильтры
            if source:
                query = query.filter(Vacancy.source == source)

            if company:
                query = query.filter(
                    Vacancy.company.ilike(f'%{company}%')
                )

            # Подсчет общего количества
            total = query.count()

            # Пагинация
            offset = (page - 1) * per_page
            vacancies = query.offset(offset).limit(per_page).all()

            return {
                'vacancies': [SearchUtils.vacancy_to_dict(v) for v in vacancies],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        finally:
            session.close()

    def clear_all_vacancies(self):
        """Очистка всех вакансий"""
        session = Session()
        try:
            count_before = session.query(Vacancy).count()
            deleted_count = session.query(Vacancy).delete()
            session.commit()

            print(f"🗑️ База данных очищена! Удалено {deleted_count} вакансий")

            return {
                'success': True,
                'message': 'База данных успешно очищена',
                'deleted_count': deleted_count,
                'count_before': count_before
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_total_count(self):
        """Получить общее количество вакансий"""
        session = Session()
        try:
            return session.query(Vacancy).count()
        finally:
            session.close()