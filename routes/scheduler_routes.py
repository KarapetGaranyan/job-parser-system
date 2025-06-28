from flask import Blueprint, jsonify, request, session
from services.scheduler_service import SchedulerService

scheduler_bp = Blueprint('scheduler', __name__, url_prefix='/api/scheduler')


def check_auth():
    """Проверка авторизации"""
    return 'user' in session


def check_admin():
    """Проверка прав администратора"""
    return session.get('role') == 'admin'


@scheduler_bp.route('/status')
def get_status():
    """Получение статуса планировщика"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    try:
        scheduler_service = SchedulerService()
        status = scheduler_service.get_status()

        return jsonify({
            'success': True,
            'running': status.get('running', False),
            'jobs': status.get('jobs', {}),
            'total_jobs': len(status.get('jobs', {})),
            'last_check': status.get('last_check')
        })

    except Exception as e:
        print(f"❌ Ошибка получения статуса планировщика: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'running': False,
            'jobs': {}
        }), 500


@scheduler_bp.route('/start', methods=['POST'])
def start_scheduler():
    """Запуск планировщика"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    if not check_admin():
        return jsonify({'error': 'Необходимы права администратора'}), 403

    try:
        scheduler_service = SchedulerService()
        result = scheduler_service.start()

        return jsonify({
            'success': True,
            'message': 'Планировщик успешно запущен',
            'status': result
        })

    except Exception as e:
        print(f"❌ Ошибка запуска планировщика: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scheduler_bp.route('/stop', methods=['POST'])
def stop_scheduler():
    """Остановка планировщика"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    if not check_admin():
        return jsonify({'error': 'Необходимы права администратора'}), 403

    try:
        scheduler_service = SchedulerService()
        result = scheduler_service.stop()

        return jsonify({
            'success': True,
            'message': 'Планировщик остановлен',
            'status': result
        })

    except Exception as e:
        print(f"❌ Ошибка остановки планировщика: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scheduler_bp.route('/add-search-job', methods=['POST'])
def add_search_job():
    """Добавление задачи автопоиска"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    try:
        data = request.get_json() or {}

        keywords = data.get('keywords', '').strip()
        interval_minutes = int(data.get('interval_minutes', 120))
        city = data.get('city', '').strip()
        limit = int(data.get('limit', 20))
        run_immediately = data.get('run_immediately', False)

        if not keywords:
            return jsonify({
                'success': False,
                'error': 'Не указаны ключевые слова для поиска'
            }), 400

        if interval_minutes < 1:
            return jsonify({
                'success': False,
                'error': 'Минимальный интервал: 1 минута'
            }), 400

        scheduler_service = SchedulerService()
        job_id = scheduler_service.add_search_job(
            keywords=keywords,
            interval_minutes=interval_minutes,
            city=city,
            limit=limit,
            run_immediately=run_immediately
        )

        return jsonify({
            'success': True,
            'message': f'Задача автопоиска добавлена (ID: {job_id})',
            'job_id': job_id
        })

    except Exception as e:
        print(f"❌ Ошибка добавления задачи: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scheduler_bp.route('/remove-job/<job_id>', methods=['DELETE'])
def remove_job(job_id):
    """Удаление задачи"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    try:
        scheduler_service = SchedulerService()
        result = scheduler_service.remove_job(job_id)

        return jsonify({
            'success': True,
            'message': f'Задача {job_id} удалена',
            'result': result
        })

    except Exception as e:
        print(f"❌ Ошибка удаления задачи {job_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scheduler_bp.route('/run-job-now/<job_id>', methods=['POST'])
def run_job_now(job_id):
    """Запуск задачи немедленно"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    try:
        scheduler_service = SchedulerService()
        result = scheduler_service.run_job_now(job_id)

        return jsonify({
            'success': True,
            'message': f'Задача {job_id} запущена',
            'result': result
        })

    except Exception as e:
        print(f"❌ Ошибка запуска задачи {job_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scheduler_bp.route('/clear-all-jobs', methods=['DELETE'])
def clear_all_jobs():
    """Очистка всех задач"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    if not check_admin():
        return jsonify({'error': 'Необходимы права администратора'}), 403

    try:
        scheduler_service = SchedulerService()
        result = scheduler_service.clear_all_jobs()

        return jsonify({
            'success': True,
            'message': 'Все задачи удалены',
            'deleted_count': result.get('deleted_count', 0)
        })

    except Exception as e:
        print(f"❌ Ошибка очистки всех задач: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scheduler_bp.route('/jobs')
def get_jobs():
    """Получение списка всех задач"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    try:
        scheduler_service = SchedulerService()
        jobs = scheduler_service.get_all_jobs()

        return jsonify({
            'success': True,
            'jobs': jobs,
            'total': len(jobs)
        })

    except Exception as e:
        print(f"❌ Ошибка получения списка задач: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'jobs': {}
        }), 500