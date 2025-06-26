import sys
import json
import os
from parsers.hh_api import fetch_hh_vacancies
from parsers.superjob_api import fetch_superjob_vacancies

def parse_salary(s):
    if not s:
        return 0
    s = str(s).replace('от', '').replace('до', '').replace('-', '').replace(' ', '').replace('₽', '').replace('руб', '')
    try:
        return int(''.join(filter(str.isdigit, s)))
    except Exception:
        return 0

def load_existing(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def main():
    site = input('Введите название сайта для поиска вакансии (HH или SuperJob или both): ').strip().lower()
    vacancy = input('Введите название вакансии: ').strip()
    count = int(input('Введите количество вакансий: ').strip())
    sort = input('Отсортировать вакансии по зарплате? (Yes / No): ').strip().lower()

    results = []
    filename = ''
    if site == 'hh':
        results = fetch_hh_vacancies(vacancy, per_page=count)
        results = [{
            'title': v['name'],
            'company': v['employer']['name'],
            'salary': str(v.get('salary', {}).get('from', '')) if v.get('salary') else '',
            'description': ((v.get('snippet', {}).get('responsibility') or '')[:200] +
                            ('...' if v.get('snippet', {}).get('responsibility') and len(v.get('snippet', {}).get('responsibility')) > 200 else '')),
            'link': v.get('alternate_url', '')
        } for v in results]
        filename = 'res_HH.json'
    elif site == 'superjob':
        sj_results = fetch_superjob_vacancies(vacancy, vacancies_count=count)
        results = [{
            'title': v.get('title', ''),
            'company': v.get('company', ''),
            'salary': v.get('salary', ''),
            'description': (v.get('description', '')[:200] + ('...' if v.get('description') and len(v.get('description')) > 200 else '')),
            'link': v.get('link', '')
        } for v in sj_results]
        filename = 'res_SJ.json'
    elif site == 'both':
        hh_results = fetch_hh_vacancies(vacancy, per_page=count)
        hh_results = [{
            'title': v['name'],
            'company': v['employer']['name'],
            'salary': str(v.get('salary', {}).get('from', '')) if v.get('salary') else '',
            'description': ((v.get('snippet', {}).get('responsibility') or '')[:200] +
                            ('...' if v.get('snippet', {}).get('responsibility') and len(v.get('snippet', {}).get('responsibility')) > 200 else '')),
            'link': v.get('alternate_url', '')
        } for v in hh_results]
        sj_results = fetch_superjob_vacancies(vacancy, vacancies_count=count)
        sj_results = [{
            'title': v.get('title', ''),
            'company': v.get('company', ''),
            'salary': v.get('salary', ''),
            'description': (v.get('description', '')[:200] + ('...' if v.get('description') and len(v.get('description')) > 200 else '')),
            'link': v.get('link', '')
        } for v in sj_results]
        results = hh_results + sj_results
        filename = 'res_ALL.json'
    else:
        print('Неизвестный сайт!')
        sys.exit(1)

    if sort == 'yes':
        results.sort(key=lambda v: parse_salary(v.get('salary', '')), reverse=True)

    for i, v in enumerate(results[:count], 1):
        link = v.get('link', '')
        print(f"{i}. {v['title']} | {v['company']} | {v['salary']}\n{v['description']}\n{link}\n---")

    # Сохраняем только уникальные вакансии
    if filename:
        existing = load_existing(filename)
        existing_links = set(v.get('link') for v in existing if v.get('link'))
        new_vacancies = [v for v in results[:count] if v.get('link') and v.get('link') not in existing_links]
        all_vacancies = existing + new_vacancies
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_vacancies, f, ensure_ascii=False, indent=2)
        print(f"Добавлено {len(new_vacancies)} новых вакансий. Всего в файле: {len(all_vacancies)}. Сохранено в {filename}")

if __name__ == '__main__':
    main() 