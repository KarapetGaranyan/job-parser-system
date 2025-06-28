from parsers.hh_parser import HHParser
from parsers.superjob_parser import SuperJobParser


class SearchService:
    def __init__(self):
        self.hh_parser = HHParser()
        self.sj_parser = SuperJobParser()

    def search_all_sources(self, query: str, city: str = '', limit: int = 50):
        """Поиск вакансий на всех источниках"""
        print(f"🔍 Начинаем поиск: {query}")

        results = {
            'query': query,
            'vacancies': [],
            'sources': {
                'hh': {'count': 0, 'status': 'pending'},
                'superjob': {'count': 0, 'status': 'pending'}
            },
            'total': 0
        }

        # Поиск на HH.ru
        try:
            print("📊 Парсинг HH.ru...")
            hh_vacancies = self.hh_parser.search(query, limit=limit, city=city)
            results['vacancies'].extend(hh_vacancies)
            results['sources']['hh'] = {
                'count': len(hh_vacancies),
                'status': 'success'
            }
            print(f"✅ HH.ru: {len(hh_vacancies)} вакансий")
        except Exception as e:
            print(f"❌ Ошибка HH.ru: {e}")
            results['sources']['hh'] = {
                'count': 0,
                'status': 'error',
                'error': str(e)
            }

        # Поиск на SuperJob
        try:
            print("📊 Парсинг SuperJob...")
            sj_vacancies = self.sj_parser.search(query, limit=limit, city=city)
            results['vacancies'].extend(sj_vacancies)
            results['sources']['superjob'] = {
                'count': len(sj_vacancies),
                'status': 'success'
            }
            print(f"✅ SuperJob: {len(sj_vacancies)} вакансий")
        except Exception as e:
            print(f"❌ Ошибка SuperJob: {e}")
            results['sources']['superjob'] = {
                'count': 0,
                'status': 'error',
                'error': str(e)
            }

        results['total'] = len(results['vacancies'])
        print(f"🎉 Поиск завершен. Всего: {results['total']} вакансий")

        return results