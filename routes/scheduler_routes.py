from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

scheduler_bp = Blueprint('scheduler', __name__)

_scheduler_instance = None


def get_scheduler():
    global _scheduler_instance
    if _scheduler_instance is None:
        from services.scheduler_service import SchedulerService
        _scheduler_instance = SchedulerService()
    return _scheduler_instance


@scheduler_bp.route('/status')
def scheduler_status():
    """Статус планировщика"""
    try:
        scheduler_service = get_scheduler()
        status = scheduler_service.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/start', methods=['POST', 'GET'])
def start_scheduler():
    """Запуск планировщика"""
    try:
        scheduler_service = get_scheduler()
        scheduler_service.start()
        return jsonify({'message': 'Планировщик запущен', 'status': 'started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/stop', methods=['POST', 'GET'])
def stop_scheduler():
    """Остановка планировщика"""
    try:
        scheduler_service = get_scheduler()
        scheduler_service.stop()
        return jsonify({'message': 'Планировщик остановлен', 'status': 'stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/add-search-job', methods=['POST'])
def add_search_job():
    """Добавить задачу автоматического поиска"""
    try:
        data = request.json
        keywords = data.get('keywords', '').strip()
        interval_minutes = int(data.get('interval_minutes', 60))
        city = data.get('city', '').strip()
        limit = int(data.get('limit', 20))
        run_immediately = data.get('run_immediately', False)

        if not keywords:
            return jsonify({'error': 'Не указаны ключевые слова для поиска'}), 400

        if interval_minutes < 1:
            return jsonify({'error': 'Минимальный интервал: 1 минута'}), 400

        # Создаем уникальное имя задачи
        import time
        job_id = f'auto_search_{int(time.time())}'

        scheduler_service = get_scheduler()

        # Создаем функцию поиска с параметрами
        def search_function():
            return scheduler_service._custom_search_job(keywords, city, limit)

        # Добавляем задачу
        scheduler_service.scheduler.add_job(
            func=search_function,
            job_id=job_id,
            interval_minutes=interval_minutes,
            run_immediately=run_immediately
        )

        keywords_list = [kw.strip() for kw in keywords.split('\n') if kw.strip()]
        city_info = f" в городе {city}" if city else ""

        return jsonify({
            'message': f'Настроен автопоиск по {len(keywords_list)} ключевым словам{city_info} каждые {interval_minutes} мин',
            'job_id': job_id,
            'keywords_count': len(keywords_list),
            'interval_minutes': interval_minutes,
            'city': city,
            'limit': limit
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/remove-job/<job_id>', methods=['POST', 'DELETE'])
def remove_job(job_id):
    """Удалить задачу"""
    try:
        scheduler_service = get_scheduler()

        if job_id not in scheduler_service.scheduler.jobs:
            return jsonify({'error': f'Задача "{job_id}" не найдена'}), 404

        # Удаляем задачу напрямую из словаря
        del scheduler_service.scheduler.jobs[job_id]
        print(f"🗑️ Удалена задача '{job_id}'")

        return jsonify({
            'message': f'Задача поиска "{job_id}" удалена',
            'job_id': job_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/run-job-now/<job_id>', methods=['POST'])
def run_job_now(job_id):
    """Запустить задачу немедленно"""
    try:
        scheduler_service = get_scheduler()

        if job_id not in scheduler_service.scheduler.jobs:
            return jsonify({'error': f'Задача "{job_id}" не найдена'}), 404

        # Устанавливаем время выполнения на сейчас
        job = scheduler_service.scheduler.jobs[job_id]
        job['next_run'] = datetime.now()

        return jsonify({
            'message': f'Поиск вакансий запущен немедленно',
            'job_id': job_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@scheduler_bp.route('/clear-all-jobs', methods=['POST', 'DELETE'])
def clear_all_jobs():
    """Очистить все задачи"""
    try:
        scheduler_service = get_scheduler()
        deleted_count = scheduler_service.clear_all_jobs()

        return jsonify({
            'message': f'Все задачи очищены. Удалено: {deleted_count}',
            'deleted_count': deleted_count
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500