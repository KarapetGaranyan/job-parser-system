from flask import Flask, render_template, request, send_file, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Vacancy
from utils.search import search_vacancies_query
from utils.export import export_vacancies_to_csv
import os
import requests
from bs4 import BeautifulSoup
from parsers.superjob_api import fetch_superjob_vacancies
import threading
from scheduler.updater import update_vacancies

app = Flask(__name__)
engine = create_engine('sqlite:///vacancies.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/', methods=['GET', 'POST'])
def index():
    session = Session()
    query = request.args.get('query', '')
    location = request.args.get('location', '')
    company = request.args.get('company', '')
    source = request.args.get('site', 'all')  # Получаем выбранный сайт: 'hh', 'superjob', 'all'
    page = int(request.args.get('page', 1))
    try:
        per_page = int(request.args.get('per_page', 10))
        if per_page not in [10, 20, 50, 100]:
            per_page = 10
    except Exception:
        per_page = 10
    q = search_vacancies_query(session, query, location, company, source)
    total = q.count()
    vacancies = q.offset((page-1)*per_page).limit(per_page).all()
    # Сохраняем последний поисковый запрос пользователя
    try:
        with open('last_query.txt', 'w', encoding='utf-8') as f:
            f.write(query)
    except Exception as e:
        print(f'Ошибка при сохранении поискового запроса: {e}')
    session.close()
    return render_template('index.html', vacancies=vacancies, page=page, total=total, per_page=per_page, query=query, location=location, company=company, source=source)

@app.route('/export')
def export():
    session = Session()
    query = request.args.get('query', '')
    location = request.args.get('location', '')
    company = request.args.get('company', '')
    q = search_vacancies_query(session, query, location, company)
    vacancies = q.all()
    filename = 'vacancies_export.csv'
    export_vacancies_to_csv(vacancies, filename)
    session.close()
    return send_file(filename, as_attachment=True)

@app.route('/api/fast_hh_search', methods=['POST'])
def fast_hh_search():
    data = request.json
    vacancy = data.get('vacancy', '')
    count = int(data.get('count', 10))
    results = []
    seen_links = set()
    page = 0
    headers = {'User-Agent': 'Mozilla/5.0'}
    max_pages = 20
    while page < max_pages and len(results) < count:
        url = f'https://hh.ru/search/vacancy?text={vacancy}&area=1&page={page}'
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'})
        if not items:
            break
        for item in items:
            if len(results) >= count:
                break
            title_tag = item.find('a', attrs={'data-qa': 'serp-item__title'})
            if not title_tag:
                title_tag = item.find('a', class_=lambda x: x and 'magritte-link' in x)
            if not title_tag:
                continue
            title = title_tag.text.strip()
            link = title_tag['href'] if title_tag.has_attr('href') else ''
            if link in seen_links:
                continue
            seen_links.add(link)
            company_tag = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
            if not company_tag:
                company_tag = item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
            company = company_tag.text.strip() if company_tag else ''
            salary_tag = item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            if not salary_tag:
                salary_tag = item.find('span', attrs={'data-qa': 'vacancy-salary-compensation-type-net'})
            salary = salary_tag.text.strip() if salary_tag else ''
            desc_tag = item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'})
            description = desc_tag.text.strip() if desc_tag else ''
            vac = {
                'title': title,
                'link': link,
                'company': company,
                'salary': salary if salary else 'Зарплата не указана',
                'description': description,
                'published_at': '',
                'source': 'hh'
            }
            results.append(vac)
        page += 1
    return jsonify({'vacancies': results})

@app.route('/api/fast_superjob_search', methods=['POST'])
def fast_superjob_search():
    data = request.json
    vacancy = data.get('vacancy', '')
    count = int(data.get('count', 10))
    sj_results = fetch_superjob_vacancies(vacancy, vacancies_count=count)
    # Обрезаем до count и делаем формат компактным
    results = [{
        'title': v.get('title', ''),
        'company': v.get('company', ''),
        'salary': v.get('salary', ''),
        'description': (v.get('description', '')[:200] + ('...' if v.get('description') and len(v.get('description')) > 200 else '')),
        'link': v.get('link', '') or v.get('url', ''),
        'published_at': v.get('published_at', ''),
        'source': 'superjob'
    } for v in sj_results[:count]]
    return jsonify({'vacancies': results})

@app.route('/api/fast_search_all', methods=['POST'])
def fast_search_all():
    data = request.json
    vacancy = data.get('vacancy', '')
    count = int(data.get('count', 10))
    # HH
    hh_results = []
    seen_links = set()
    page = 0
    headers = {'User-Agent': 'Mozilla/5.0'}
    max_pages = 20
    while page < max_pages and len(hh_results) < count:
        url = f'https://hh.ru/search/vacancy?text={vacancy}&area=1&page={page}'
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'})
        if not items:
            break
        for item in items:
            if len(hh_results) >= count:
                break
            title_tag = item.find('a', attrs={'data-qa': 'serp-item__title'})
            if not title_tag:
                title_tag = item.find('a', class_=lambda x: x and 'magritte-link' in x)
            if not title_tag:
                continue
            title = title_tag.text.strip()
            link = title_tag['href'] if title_tag.has_attr('href') else ''
            if link in seen_links:
                continue
            seen_links.add(link)
            company_tag = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
            if not company_tag:
                company_tag = item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
            company = company_tag.text.strip() if company_tag else ''
            salary_tag = item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            if not salary_tag:
                salary_tag = item.find('span', attrs={'data-qa': 'vacancy-salary-compensation-type-net'})
            salary = salary_tag.text.strip() if salary_tag else ''
            desc_tag = item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'})
            description = desc_tag.text.strip() if desc_tag else ''
            vac = {
                'title': title,
                'link': link,
                'company': company,
                'salary': salary if salary else 'Зарплата не указана',
                'description': description,
                'published_at': '',
                'source': 'hh'
            }
            hh_results.append(vac)
        page += 1
    # SuperJob
    sj_results = fetch_superjob_vacancies(vacancy, vacancies_count=count)
    sj_results = [{
        'title': v.get('title', ''),
        'company': v.get('company', ''),
        'salary': v.get('salary', ''),
        'description': (v.get('description', '')[:200] + ('...' if v.get('description') and len(v.get('description')) > 200 else '')),
        'link': v.get('link', '') or v.get('url', ''),
        'published_at': v.get('published_at', ''),
        'source': 'superjob'
    } for v in sj_results[:count]]
    results = hh_results + sj_results
    return jsonify({'vacancies': results})

@app.route('/trigger_update', methods=['POST'])
def trigger_update():
    def run_update():
        update_vacancies()
    thread = threading.Thread(target=run_update)
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/clear_db', methods=['POST'])
def clear_db():
    session = Session()
    try:
        session.query(Vacancy).delete()
        session.commit()
        return jsonify({'status': 'ok'})
    except Exception as e:
        session.rollback()
        return jsonify({'status': 'error', 'error': str(e)})
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True) 