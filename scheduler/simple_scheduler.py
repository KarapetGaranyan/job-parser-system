import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SimpleScheduler:
    """Простой планировщик задач для поиска вакансий"""

    def __init__(self):
        self.jobs = {}
        self.running = False
        self.thread = None

    def start(self):
        """Запуск планировщика"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("🕐 Планировщик запущен")

    def stop(self):
        """Остановка планировщика"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("🕐 Планировщик остановлен")

    def add_job(self, func: Callable, job_id: str, interval_minutes: int = 60,
                run_immediately: bool = False, **kwargs):
        """Добавить задачу"""
        next_run = datetime.now()
        if not run_immediately:
            next_run += timedelta(minutes=interval_minutes)

        self.jobs[job_id] = {
            'func': func,
            'interval': timedelta(minutes=interval_minutes),
            'next_run': next_run,
            'kwargs': kwargs,
            'last_run': None,
            'run_count': 0
        }

        print(f"📋 Добавлена задача '{job_id}' с интервалом {interval_minutes} мин")

    def get_jobs_status(self) -> Dict[str, Any]:
        """Получить статус всех задач"""
        status = {}
        for job_id, job in self.jobs.items():
            status[job_id] = {
                'next_run': job['next_run'].strftime('%Y-%m-%d %H:%M:%S'),
                'last_run': job['last_run'].strftime('%Y-%m-%d %H:%M:%S') if job['last_run'] else 'Никогда',
                'run_count': job['run_count'],
                'interval_minutes': int(job['interval'].total_seconds() / 60)
            }
        return status

    def _run(self):
        """Основной цикл планировщика"""
        while self.running:
            try:
                current_time = datetime.now()

                for job_id, job in list(self.jobs.items()):
                    if current_time >= job['next_run']:
                        self._execute_job(job_id, job)

                time.sleep(10)  # Проверяем каждые 10 секунд

            except Exception as e:
                print(f"❌ Ошибка в планировщике: {e}")
                time.sleep(30)

    def _execute_job(self, job_id: str, job: Dict[str, Any]):
        """Выполнить задачу"""
        try:
            print(f"▶️ Выполняется задача '{job_id}' в {datetime.now().strftime('%H:%M:%S')}")

            result = job['func'](**job['kwargs'])

            job['last_run'] = datetime.now()
            job['run_count'] += 1
            job['next_run'] = datetime.now() + job['interval']

            print(f"✅ Задача '{job_id}' выполнена успешно в {job['last_run'].strftime('%H:%M:%S')}")

        except Exception as e:
            print(f"❌ Ошибка выполнения задачи '{job_id}': {e}")
            job['next_run'] = datetime.now() + timedelta(minutes=10)