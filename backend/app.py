from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests as ext_requests
from bs4 import BeautifulSoup

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

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
        vacancies.append({
            'title': title,
            'link': link,
            'company': company,
            'salary': salary
        })

    return jsonify({'vacancies': vacancies})

def parse_superjob(vacancy):
    url = f'https://www.superjob.ru/vacancy/search/?keywords={vacancy}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = ext_requests.get(url, headers=headers, timeout=7)
        soup = BeautifulSoup(response.text, 'html.parser')
        vacancies = []
        for item in soup.find_all('div', attrs={'class': 'f-test-vacancy-item'}):
            title_tag = item.find('a', attrs={'target': '_blank'})
            if not title_tag:
                continue
            title = title_tag.text.strip()
            link = 'https://www.superjob.ru' + title_tag['href']
            company_tag = item.find('span', attrs={'class': 'f-test-text-vacancy-item-company-name'})
            company = company_tag.text.strip() if company_tag else ''
            salary_tag = item.find('span', attrs={'class': 'f-test-text-company-item-salary'})
            salary = salary_tag.text.strip() if salary_tag else 'Зарплата не указана'
            vacancies.append({
                'title': title,
                'link': link,
                'company': company,
                'salary': salary,
                'source': 'superjob'
            })
        return vacancies
    except Exception as e:
        print(f'Ошибка при парсинге SuperJob: {e}')
        return []

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
        hh_vacancies.append({
            'title': title,
            'link': link,
            'company': company,
            'salary': salary if salary else 'Зарплата не указана',
            'source': 'hh'
        })

    # SuperJob
    sj_vacancies = parse_superjob(vacancy)
    return jsonify({'vacancies': hh_vacancies + sj_vacancies})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)