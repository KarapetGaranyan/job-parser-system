import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from threading import Thread
import uuid
from services.search_service import SearchService


class SchedulerService:
    """Сервис для управления планировщиком задач"""

    def __init__(self):
        self.scheduler_file = 'scheduler_data.json'
        self.is_running = False
        self.jobs = {}
        self.load_data()

    def load_data(self):
        """Загрузка данных планировщика из файла"""
        try:
            if os.path.exists(self.scheduler_file):
                with open(self.scheduler_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.is_running = data.get('running', False)
                    self.jobs = data.get('jobs', {})
                    print(f"📋 Загружено {len(self.jobs)} задач планировщика")
            else:
                self.save_data()
                print("📋 Создан новый файл планировщика")
        except Exception as e:
            print(f"❌ Ошибка загрузки данных планировщика: {e}")
            self.is_running = False
            self.jobs = {}

    def save_data(self):
        """Сохранение данных планировщика в файл"""
        try:
            data = {
                'running': self.is_running,
                'jobs': self.jobs,
                'last_update': datetime.now().isoformat()
            }

            with open(self.scheduler_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"❌ Ошибка сохранения данных планировщика: {e}")

    def get_status(self) -> Dict:
        """Получение статуса планировщика"""
        return {
            'running': self.is_running,
            'jobs': self.jobs,
            'jobs_count': len(self.jobs),
            'last_check': datetime.now().isoformat()
        }

    def start(self) -> Dict:
        """Запуск планировщика"""
        if self.is_running:
            return {'status': 'already_running', 'message': 'Планировщик уже запущен'}

        self.is_running = True
        self.save_data()

        # Запускаем планировщик в отдельном потоке
        scheduler_thread = Thread(target=self._scheduler_loop, daemon=True)
        scheduler_thread.start()

        print("🟢 Планировщик запущен")
        return {'status': 'started', 'message': 'Планировщик успешно запущен'}

    def stop(self) -> Dict:
        """Остановка планировщика"""
        if not self.is_running:
            return {'status': 'already_stopped', 'message': 'Планировщик уже остановлен'}

        self.is_running = False
        self.save_data()

        print("🔴 Планировщик остановлен")
        return {'status': 'stopped', 'message': 'Планировщик остановлен'}

    def add_search_job(self, keywords: str, interval_minutes: int,
                       city: str = '', limit: int = 20, run_immediately: bool = False) -> str:
        """Добавление задачи автопоиска"""
        job_id = f"search_{uuid.uuid4().hex[:8]}"

        # Парсим ключевые слова
        keywords_list = [kw.strip() for kw in keywords.split('\n') if kw.strip()]

        next_run = datetime.now()
        if not run_immediately:
            next_run += timedelta(minutes=interval_minutes)

        job = {
            'id': job_id,
            'type': 'search',
            'keywords': keywords_list,
            'city': city,
            'limit': limit,
            'interval_minutes': interval_minutes,
            'next_run': next_run.isoformat(),
            'last_run': 'Никогда',
            'run_count': 0,
            'created': datetime.now().isoformat(),
            'status': 'active'
        }

        self.jobs[job_id] = job
        self.save_data()

        print(f"➕ Добавлена задача автопоиска: {job_id}")

        # Запускаем сразу, если нужно
        if run_immediately and self.is_running:
            self.run_job_now(job_id)

        return job_id

    def remove_job(self, job_id: str) -> Dict:
        """Удаление задачи"""
        if job_id not in self.jobs:
            return {'status': 'not_found', 'message': f'Задача {job_id} не найдена'}

        del self.jobs[job_id]
        self.save_data()

        print(f"🗑️ Удалена задача: {job_id}")
        return {'status': 'removed', 'message': f'Задача {job_id} удалена'}

    def run_job_now(self, job_id: str) -> Dict:
        """Запуск задачи немедленно"""
        if job_id not in self.jobs:
            return {'status': 'not_found', 'message': f'Задача {job_id} не найдена'}

        job = self.jobs[job_id]

        try:
            print(f"🏃‍♂️ Запуск задачи: {job_id}")

            if job['type'] == 'search':
                self._execute_search_job(job)

            # Обновляем информацию о запуске
            job['last_run'] = datetime.now().isoformat()
            job['run_count'] = job.get('run_count', 0) + 1

            # Планируем следующий запуск
            next_run = datetime.now() + timedelta(minutes=job['interval_minutes'])
            job['next_run'] = next_run.isoformat()

            self.save_data()

            return {'status': 'executed', 'message': f'Задача {job_id} выполнена'}

        except Exception as e:
            print(f"❌ Ошибка выполнения задачи {job_id}: {e}")
            return {'status': 'error', 'message': str(e)}

    def clear_all_jobs(self) -> Dict:
        """Очистка всех задач"""
        deleted_count = len(self.jobs)
        self.jobs = {}
        self.save_data()

        print(f"🗑️ Удалены все задачи планировщика ({deleted_count} шт.)")
        return {'status': 'cleared', 'deleted_count': deleted_count}

    def get_all_jobs(self) -> Dict:
        """Получение всех задач"""
        return self.jobs.copy()

    def _scheduler_loop(self):
        """Основной цикл планировщика"""
        print("🔄 Запущен цикл планировщика")

        while self.is_running:
            try:
                current_time = datetime.now()

                # Проверяем все задачи
                for job_id, job in list(self.jobs.items()):
                    if job.get('status') != 'active':
                        continue

                    next_run_str = job.get('next_run')
                    if not next_run_str:
                        continue

                    try:
                        next_run = datetime.fromisoformat(next_run_str)

                        # Время выполнить задачу?
                        if current_time >= next_run:
                            print(f"⏰ Время выполнения задачи: {job_id}")
                            self.run_job_now(job_id)

                    except Exception as e:
                        print(f"❌ Ошибка обработки задачи {job_id}: {e}")

                # Сохраняем данные и ждем
                self.save_data()
                time.sleep(30)  # Проверяем каждые 30 секунд

            except Exception as e:
                print(f"❌ Ошибка в цикле планировщика: {e}")
                time.sleep(60)  # При ошибке ждем минуту

        print("🔴 Цикл планировщика остановлен")

    def _execute_search_job(self, job: Dict):
        """Выполнение задачи поиска"""
        keywords = job.get('keywords', [])
        city = job.get('city', '')
        limit = job.get('limit', 20)

        search_service = SearchService()

        total_found = 0

        for keyword in keywords:
            try:
                print(f"🔍 Автопоиск: '{keyword}'" + (f" в {city}" if city else ""))

                results = search_service.search_all_sources(
                    query=keyword,
                    city=city,
                    limit=limit // len(keywords) if len(keywords) > 1 else limit
                )

                found_count = results.get('total', 0)
                total_found += found_count

                print(f"✅ Найдено {found_count} вакансий по запросу '{keyword}'")

                # Небольшая пауза между запросами
                time.sleep(2)

            except Exception as e:
                print(f"❌ Ошибка поиска по '{keyword}': {e}")

        print(f"🎯 Автопоиск завершен. Всего найдено: {total_found} вакансий")

        # Обновляем статистику задачи
        if 'stats' not in job:
            job['stats'] = {}

        job['stats']['last_execution'] = {
            'time': datetime.now().isoformat(),
            'found': total_found,
            'keywords_processed': len(keywords)
        }