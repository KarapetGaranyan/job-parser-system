from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests as ext_requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import csv
import io

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

engine = create_engine('sqlite:///vacancies.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    link = Column(Text)
    company = Column(String(256))
    salary = Column(String(128))
    source = Column(String(32))

Base.metadata.create_all(engine)

def save_vacancy_to_db(vac):
    session = Session()
    exists = session.query(Vacancy).filter_by(link=vac['link']).first()
    if not exists:
        vacancy = Vacancy(
            title=vac['title'],
            link=vac['link'],
            company=vac['company'],
            salary=vac['salary'],
            source=vac['source']
        )
        session.add(vacancy)
        session.commit()
    session.close()

@app.route('/')
def home():
    return jsonify({
        'message': 'Job Parser System API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/hh_search', methods=['POST'])
def hh_search():
    data = request.json
    vacancy = data.get('vacancy', '')
    if not vacancy:
        return jsonify({'error': 'Не указано название вакансии'}), 400

    url = f'https://hh.ru/search/vacancy?text={vacancy}&area=1'
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = ext_requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({'error': 'Ошибка при запросе к HH.ru'}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    vacancies = []
    for item in soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'}):
        title_tag = item.find('a', attrs={'data-qa': 'serp-item__title'})
        if not title_tag:
            title_tag = item.find('a', class_=lambda x: x and 'magritte-link' in x)
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link = title_tag['href']
        company_tag = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
        if not company_tag:
            company_tag = item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
        company = company_tag.text.strip() if company_tag else ''
        # Зарплата
        salary_tag = item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        if not salary_tag:
            salary_tag = item.find('span', attrs={'data-qa': 'vacancy-salary-compensation-type-net'})
        salary = salary_tag.text.strip() if salary_tag else ''

        # Если зарплата не найдена, пробуем получить с детальной страницы
        if not salary:
            try:
                detail_resp = ext_requests.get(link, headers=headers, timeout=5)
                if detail_resp.status_code == 200:
                    detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                    salary_detail = detail_soup.find('span', attrs={'data-qa': 'vacancy-salary-compensation-type-net'})
                    if salary_detail:
                        salary = salary_detail.text.strip()
            except Exception as e:
                salary = ''
        vac = {
            'title': title,
            'link': link,
            'company': company,
            'salary': salary if salary else 'Зарплата не указана',
            'source': 'hh'
        }
        vacancies.append(vac)
        save_vacancy_to_db(vac)

    return jsonify({'vacancies': vacancies})

def get_superjob_vacancies(search_word, vacancies_count=20):
    url = 'https://api.superjob.ru/2.0/vacancies'
    secret = 'v3.r.137222938.adcc1bf5602cc5a2c697d63eb9c580dd5029f96f.049aae965267ebe71bbc7c587187da62cdbc560e'
    per_page = 20
    page = 0
    result = []
    headers = {
        'X-Api-App-Id': secret,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    while per_page * page < vacancies_count:
        params = {
            'keyword': search_word,
            'page': page,
            'count': per_page
        }
        response = ext_requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            for obj in data.get('objects', []):
                salary = ''
                if obj.get('payment_from', 0) and obj.get('payment_to', 0):
                    salary = f"{obj['payment_from']} - {obj['payment_to']} {obj.get('currency', '')}"
                elif obj.get('payment_from', 0):
                    salary = f"от {obj['payment_from']} {obj.get('currency', '')}"
                elif obj.get('payment_to', 0):
                    salary = f"до {obj['payment_to']} {obj.get('currency', '')}"
                else:
                    salary = 'Зарплата не указана'
                vac = {
                    'title': obj.get('profession', ''),
                    'link': obj.get('link', ''),
                    'company': obj.get('firm_name', ''),
                    'salary': salary,
                    'source': 'superjob'
                }
                result.append(vac)
                save_vacancy_to_db(vac)
            if not data.get('more', False):
                break
            page += 1
        else:
            break
    return result

@app.route('/api/search_all', methods=['POST'])
def search_all():
    data = request.json
    vacancy = data.get('vacancy', '')
    if not vacancy:
        return jsonify({'error': 'Не указано название вакансии'}), 400

    # HH.ru
    url = f'https://hh.ru/search/vacancy?text={vacancy}&area=1'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = ext_requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    hh_vacancies = []
    for item in soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'}):
        title_tag = item.find('a', attrs={'data-qa': 'serp-item__title'})
        if not title_tag:
            title_tag = item.find('a', class_=lambda x: x and 'magritte-link' in x)
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link = title_tag['href']
        company_tag = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
        if not company_tag:
            company_tag = item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
        company = company_tag.text.strip() if company_tag else ''
        salary_tag = item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        if not salary_tag:
            salary_tag = item.find('span', attrs={'data-qa': 'vacancy-salary-compensation-type-net'})
        salary = salary_tag.text.strip() if salary_tag else ''
        if not salary:
            try:
                detail_resp = ext_requests.get(link, headers=headers, timeout=5)
                if detail_resp.status_code == 200:
                    detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                    salary_detail = detail_soup.find('span', attrs={'data-qa': 'vacancy-salary-compensation-type-net'})
                    if salary_detail:
                        salary = salary_detail.text.strip()
            except Exception as e:
                salary = ''
        vac = {
            'title': title,
            'link': link,
            'company': company,
            'salary': salary if salary else 'Зарплата не указана',
            'source': 'hh'
        }
        hh_vacancies.append(vac)
        save_vacancy_to_db(vac)

    # SuperJob через API
    sj_vacancies = get_superjob_vacancies(vacancy, vacancies_count=20)
    return jsonify({'vacancies': hh_vacancies + sj_vacancies})

@app.route('/api/vacancies', methods=['GET'])
def get_vacancies():
    session = Session()
    vacancies = session.query(Vacancy).all()
    result = []
    for v in vacancies:
        result.append({
            'title': v.title,
            'link': v.link,
            'company': v.company,
            'salary': v.salary,
            'source': v.source
        })
    session.close()
    return jsonify({'vacancies': result})

@app.route('/vacancies_text', methods=['GET'])
def vacancies_text():
    session = Session()
    vacancies = session.query(Vacancy).all()
    lines = []
    for v in vacancies:
        lines.append(
            f"Вакансия: {v.title}\n"
            f"Компания: {v.company}\n"
            f"Зарплата: {v.salary}\n"
            f"Ссылка: {v.link}\n"
            f"Источник: {v.source}\n"
            "-----------------------------"
        )
    session.close()
    return "<pre>" + "\n".join(lines) + "</pre>"

@app.route('/export_csv', methods=['GET'])
def export_csv():
    session = Session()
    vacancies = session.query(Vacancy).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['title', 'company', 'salary', 'link', 'source'])
    for v in vacancies:
        writer.writerow([v.title, v.company, v.salary, v.link, v.source])
    session.close()
    output.seek(0)
    # Добавляем BOM для Excel
    bom = '\ufeff'
    csv_data = bom + output.getvalue()
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=vacancies.csv'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)