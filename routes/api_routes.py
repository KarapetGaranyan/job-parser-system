from flask import Blueprint, jsonify, request, session
from services.search_service import SearchService
from services.vacancy_service import VacancyService
from services.stats_service import StatsService

api_bp = Blueprint('api', __name__, url_prefix='/api')


def check_auth():
    """Простая проверка авторизации для API"""
    return 'user' in session


@api_bp.route('/search', methods=['POST'])
def api_search():
    """API поиска вакансий"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        city = data.get('city', '')
        limit = int(data.get('limit', 50))

        if not query:
            return jsonify({'error': 'Не указан поисковый запрос'}), 400

        search_service = SearchService()
        results = search_service.search_all_sources(query, city, limit)

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/vacancies')
def api_vacancies():
    """API получения вакансий с пагинацией"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        source = request.args.get('source', '')
        company = request.args.get('company', '')

        vacancy_service = VacancyService()
        result = vacancy_service.get_vacancies_paginated(
            page=page,
            per_page=per_page,
            source=source,
            company=company
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/stats')
def api_stats():
    """API получения статистики"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    try:
        stats_service = StatsService()
        stats = stats_service.get_full_statistics()

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/health')
def api_health():
    """Проверка состояния API"""
    return jsonify({
        'status': 'ok',
        'authenticated': check_auth(),
        'user': session.get('user') if check_auth() else None
    })


@api_bp.route('/clear', methods=['POST'])
def api_clear_vacancies():
    """API для очистки всех вакансий"""
    if not check_auth():
        return jsonify({'error': 'Необходима авторизация'}), 401

    # Проверяем права администратора
    if session.get('role') != 'admin':
        return jsonify({'error': 'Недостаточно прав. Необходимы права администратора.'}), 403

    try:
        vacancy_service = VacancyService()
        result = vacancy_service.clear_all_vacancies()

        return jsonify({
            'success': True,
            'message': result['message'],
            'deleted_count': result['deleted_count']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500