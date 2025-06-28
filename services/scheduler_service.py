from scheduler.simple_scheduler import SimpleScheduler
from services.search_service import SearchService
from services.vacancy_service import VacancyService
import logging

logger = logging.getLogger(__name__)


class SchedulerService:
    """Сервис для управления автоматическими задачами поиска вакансий"""

    def __init__(self):
        self.scheduler = SimpleScheduler()
        self.search_service = SearchService()
        self.vacancy_service = VacancyService()

    def start(self):
        """Запуск планировщика"""
        print("🔍 Запуск планировщика...")
        print("▶️ Стартуем планировщик...")
        self.scheduler.start()
        print(f"✅ Планировщик запущен. Задач: {len(self.scheduler.jobs)}")

    def stop(self):
        """Остановка планировщика"""
        self.scheduler.stop()

    def get_status(self):
        """Получить статус планировщика"""
        return {
            'running': self.scheduler.running,
            'jobs': self.scheduler.get_jobs_status(),
            'debug': {
                'jobs_count': len(self.scheduler.jobs),
                'jobs_list': list(self.scheduler.jobs.keys())
            }
        }

    def clear_all_jobs(self):
        """Очистить все задачи"""
        jobs_count = len(self.scheduler.jobs)
        self.scheduler.jobs.clear()
        print(f"🗑️ Очищены все задачи планировщика. Удалено: {jobs_count}")
        return jobs_count

    def _custom_search_job(self, keywords_text, city='', limit=20):
        """Пользовательская задача поиска по ключевым словам"""
        keywords_list = [kw.strip() for kw in keywords_text.split('\n') if kw.strip()]

        print(f"🔍 Начинаем автопоиск по {len(keywords_list)} ключевым словам")

        total_found = 0
        for keyword in keywords_list:
            try:
                print(f"🔍 Поиск: '{keyword}'" + (f" в {city}" if city else ""))

                result = self.search_service.search_all_sources(
                    query=keyword,
                    city=city,
                    limit=limit
                )

                found = result.get('total', 0)
                total_found += found

                print(f"✅ '{keyword}': найдено {found} вакансий")

            except Exception as e:
                print(f"❌ Ошибка поиска '{keyword}': {e}")

        city_info = f" в {city}" if city else ""
        print(f"🎉 Автопоиск завершен{city_info}. Всего найдено: {total_found} вакансий")

        return {
            'total_found': total_found,
            'keywords_processed': len(keywords_list),
            'city': city
        }