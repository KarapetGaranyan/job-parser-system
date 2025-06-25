import json
from app import get_superjob_vacancies, save_vacancy_to_db
from app import ext_requests, BeautifulSoup
import os

def parse_hh(job_title, number_vacancies):
    headers = {'User-Agent': 'Mozilla/5.0'}
    hh_vacancies = []
    seen_links = set()
    page = 0
    while len(hh_vacancies) < number_vacancies:
        url = f'https://hh.ru/search/vacancy?text={job_title}&area=1&page={page}'
        response = ext_requests.get(url, headers=headers)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'})
        if not items:
            break
        for item in items:
            if len(hh_vacancies) >= number_vacancies:
                break
            title_tag = item.find('a', attrs={'data-qa': 'serp-item__title'})
            if not title_tag:
                continue
            title = title_tag.text.strip()
            link = title_tag['href']
            if link in seen_links:
                continue
            seen_links.add(link)
            company_tag = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
            company = company_tag.text.strip() if company_tag else ''
            salary_tag = item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            salary = salary_tag.text.strip() if salary_tag else 'Зарплата не указана'
            vac = {
                'title': title,
                'link': link,
                'company': company,
                'salary': salary,
                'source': 'hh'
            }
            hh_vacancies.append(vac)
            save_vacancy_to_db(vac)
        page += 1
    return hh_vacancies

def save_to_file(vacancies, filename='vacancies_cli.json'):
    # Загружаем старые вакансии
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            old_vacancies = json.load(f)
    else:
        old_vacancies = []
    old_links = set(v['link'] for v in old_vacancies)
    # Добавляем только новые
    new_vacancies = [v for v in vacancies if v['link'] not in old_links]
    all_vacancies = old_vacancies + new_vacancies
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_vacancies, f, ensure_ascii=False, indent=2)
    print(f'Сохранено {len(new_vacancies)} новых вакансий. Всего в файле: {len(all_vacancies)}')

def main():
    site_name = input('Введите название сайта для поиска вакансии (HH или SuperJob): ').strip().lower()
    job_title = input('Введите название вакансии: ').strip()
    number_vacancies = int(input('Введите количество вакансий: '))
    sort_vacancies = input('Отсортировать вакансии по зарплате? (Yes / No): ').strip().lower()

    if site_name == 'hh':
        vacancies = parse_hh(job_title, number_vacancies)
    elif site_name == 'superjob':
        vacancies = get_superjob_vacancies(job_title, number_vacancies)
    else:
        print('Неизвестный сайт!')
        return

    if sort_vacancies == 'yes':
        def salary_to_int(s):
            try:
                return int(s.split()[0].replace('от', '').replace('до', '').replace('-', '').replace('₽', '').replace(' ', ''))
            except:
                return 0
        vacancies = sorted(vacancies, key=lambda v: salary_to_int(v['salary']), reverse=True)

    # Сохраняем только новые вакансии
    save_to_file(vacancies)

    # Показываем только запрошенное количество
    for v in vacancies[:number_vacancies]:
        print(f"Вакансия: {v['title']}\nКомпания: {v['company']}\nЗарплата: {v['salary']}\nСсылка: {v['link']}\nИсточник: {v['source']}\n{'-'*40}")

if __name__ == '__main__':
    main() 