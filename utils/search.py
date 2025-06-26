from database.models import Vacancy
from sqlalchemy.orm import Session

def search_vacancies_query(session: Session, query: str = None, location: str = None, company: str = None, source: str = None):
    q = session.query(Vacancy)
    if query:
        q = q.filter(Vacancy.title.ilike(f'%{query}%'))
    if location:
        q = q.filter(Vacancy.location.ilike(f'%{location}%'))
    if company:
        q = q.filter(Vacancy.company.ilike(f'%{company}%'))
    if source:
        if source == 'all':
            pass
        elif source in ['hh', 'superjob']:
            q = q.filter(Vacancy.source == source)
    return q 