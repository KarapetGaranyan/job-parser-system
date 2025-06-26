from apscheduler.schedulers.background import BackgroundScheduler
from parsers.hh_api import fetch_hh_vacancies
from parsers.superjob_api import fetch_superjob_vacancies
from database.models import Vacancy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import re

def strip_tags(text):
    return re.sub(r'<.*?>', '', text) if text else ''

def get_last_query():
    try:
        with open('last_query.txt', 'r', encoding='utf-8') as f:
            return f.read().strip() or 'python'
    except FileNotFoundError:
        return 'python'

def update_vacancies():
    print("Запуск обновления вакансий...")
    engine = create_engine('sqlite:///vacancies.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    # HH.ru — собираем до 200 вакансий с перебором страниц
    search_query = get_last_query()
    all_hh = []
    page = 0
    per_page = 100
    max_vacancies = 200
    while len(all_hh) < max_vacancies:
        batch = fetch_hh_vacancies(search_query, page=page, per_page=per_page)
        if not batch:
            break
        all_hh.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    print(f"Найдено вакансий HH: {len(all_hh)}")
    added_hh = 0
    for v in all_hh:
        exists = session.query(Vacancy).filter_by(title=v['name'], company=v['employer']['name']).first()
        if not exists:
            vacancy = Vacancy(
                title=v['name'],
                company=v['employer']['name'],
                location=v.get('area', {}).get('name', ''),
                salary=str(v.get('salary', {}).get('from', '')) if v.get('salary') else '',
                description=strip_tags(v.get('snippet', {}).get('responsibility', '')),
                published_at=datetime.strptime(v['published_at'][:10], '%Y-%m-%d'),
                source='hh',
                link=v.get('alternate_url', '')
            )
            session.add(vacancy)
            added_hh += 1
            print(f"Добавлена вакансия HH: {v['name']} | {v['employer']['name']}")
    # SuperJob — собираем до 200 вакансий с перебором страниц
    all_sj = fetch_superjob_vacancies(search_query, vacancies_count=200)
    print(f"Найдено вакансий SuperJob: {len(all_sj)}")
    added_sj = 0
    for v in all_sj:
        exists = session.query(Vacancy).filter_by(title=v['title'], company=v['company']).first()
        if not exists:
            vacancy = Vacancy(
                title=v['title'],
                company=v['company'],
                location=v['location'],
                salary=v['salary'],
                description=strip_tags(v['description']),
                published_at=datetime.fromtimestamp(v['published_at']) if v['published_at'] else None,
                source='superjob',
                link=v.get('link', '')
            )
            session.add(vacancy)
            added_sj += 1
            print(f"Добавлена вакансия SuperJob: {v['title']} | {v['company']}")
    session.commit()
    session.close()
    print(f"Добавлено новых вакансий HH: {added_hh}, SuperJob: {added_sj}")
    print("Обновление завершено.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_vacancies, 'interval', hours=3)
    scheduler.start()

if __name__ == '__main__':
    update_vacancies()  # Запуск обновления сразу при старте
    start_scheduler()
    import time
    print('Планировщик запущен. Для остановки нажмите Ctrl+C.')
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print('Остановка планировщика.') 