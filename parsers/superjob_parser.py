import requests
from .base_parser import BaseParser
from typing import List, Dict
import os
import time


class SuperJobParser(BaseParser):
    """Парсер для SuperJob через API"""

    def __init__(self):
        super().__init__('superjob')
        self.api_url = 'https://api.superjob.ru/2.0/vacancies'
        self.secret_key = os.getenv(
            'SUPERJOB_SECRET',
            'v3.r.137222938.adcc1bf5602cc5a2c697d63eb9c580dd5029f96f.049aae965267ebe71bbc7c587187da62cdbc560e'
        )
        self.headers = {
            'X-Api-App-Id': self.secret_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def search(self, query: str, limit: int = 20, city: str = '') -> List[Dict]:
        """Поиск вакансий через SuperJob API с фильтром по городу"""
        print(f"🔍 Поиск в SuperJob: {query}" + (f" в городе {city}" if city else ""))
        vacancies = []
        page = 0
        per_page = min(20, limit)

        try:
            while len(vacancies) < limit:
                params = {
                    'keyword': query,
                    'page': page,
                    'count': per_page
                }

                # ДОБАВИТЬ ОБРАБОТКУ ГОРОДА:
                if city:
                    params['keyword'] = f"{query} {city}"
                    print(f"📍 Поиск с городом: '{query} {city}'")
                else:
                    params['keyword'] = query
                    print(f"🌍 Поиск без города: '{query}'")

                # Остальной код остается без изменений
                response = requests.get(
                    self.api_url,
                    headers=self.headers,
                    params=params,
                    timeout=10
                )
                response.raise_for_status()

                data = response.json()
                objects = data.get('objects', [])

                if not objects:
                    break

                for obj in objects:
                    if len(vacancies) >= limit:
                        break

                    try:
                        vacancy_data = self._parse_vacancy_object(obj)
                        if vacancy_data:
                            vacancies.append(vacancy_data)
                            self.save_vacancy(vacancy_data)

                    except Exception as e:
                        print(f"Ошибка парсинга вакансии SuperJob: {e}")
                        continue

                if not data.get('more', False):
                    break

                page += 1
                time.sleep(0.5)  # Задержка между запросами

        except Exception as e:
            print(f"Ошибка поиска в SuperJob: {e}")

        print(f"✅ SuperJob: найдено {len(vacancies)} вакансий")
        return vacancies

    def _parse_vacancy_object(self, obj: Dict) -> Dict:
        """Парсинг объекта вакансии из API"""
        # Формирование зарплаты
        salary_parts = []
        if obj.get('payment_from'):
            salary_parts.append(f"от {obj['payment_from']}")
        if obj.get('payment_to'):
            salary_parts.append(f"до {obj['payment_to']}")
        if obj.get('currency'):
            salary_parts.append(obj['currency'])

        salary = ' '.join(salary_parts) if salary_parts else 'Не указана'

        return {
            'title': obj.get('profession', 'Не указано'),
            'link': obj.get('link', ''),
            'company': obj.get('firm_name', 'Не указана'),
            'salary': salary,
            'source': 'superjob'
        }