import requests
from bs4 import BeautifulSoup
from .base_parser import BaseParser
from typing import List, Dict
import time


class HHParser(BaseParser):
    """Парсер для сайта HH.ru"""

    def __init__(self):
        super().__init__('hh')
        self.base_url = 'https://hh.ru'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search(self, query: str, limit: int = 20, city: str = '') -> List[Dict]:
        """Поиск вакансий на HH.ru с фильтром по городу"""
        print(f"🔍 Поиск на HH.ru: {query}" + (f" в городе {city}" if city else ""))
        vacancies = []

        try:
            # Формируем URL для поиска
            search_url = f'{self.base_url}/search/vacancy'
            params = {
                'text': query,
                'per_page': min(limit, 50)
            }

            # ДОБАВИТЬ ОБРАБОТКУ ГОРОДА:
            if city:
                params['area'] = city
                print(f"📍 Применен фильтр по городу ID: {city}")

            response = requests.get(search_url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем контейнеры с вакансиями
            vacancy_items = soup.find_all('div', {'data-qa': 'vacancy-serp__vacancy'})

            for item in vacancy_items[:limit]:
                try:
                    vacancy_data = self._parse_vacancy_item(item)
                    if vacancy_data:
                        vacancies.append(vacancy_data)
                        self.save_vacancy(vacancy_data)

                except Exception as e:
                    print(f"Ошибка парсинга вакансии HH: {e}")
                    continue

                # Небольшая задержка между запросами
                time.sleep(0.3)

        except Exception as e:
            print(f"Ошибка поиска на HH.ru: {e}")

        print(f"✅ HH.ru: найдено {len(vacancies)} вакансий")
        return vacancies

    def _parse_vacancy_item(self, item) -> Dict:
        """Парсинг отдельной вакансии"""
        # Название и ссылка
        title_tag = item.find('a', {'data-qa': 'serp-item__title'})
        if not title_tag:
            title_tag = item.find('a', class_=lambda x: x and 'magritte-link' in x)

        if not title_tag:
            return None

        title = title_tag.text.strip()
        link = title_tag['href']
        if not link.startswith('http'):
            link = self.base_url + link

        # Компания
        company_tag = item.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
        if not company_tag:
            company_tag = item.find('div', {'data-qa': 'vacancy-serp__vacancy-employer'})
        company = company_tag.text.strip() if company_tag else 'Не указана'

        # Зарплата
        salary_tag = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        salary = salary_tag.text.strip() if salary_tag else 'Не указана'

        return {
            'title': title,
            'link': link,
            'company': company,
            'salary': salary,
            'source': 'hh'
        }