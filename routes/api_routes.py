from flask import Blueprint, jsonify, request
from services.search_service import SearchService
from services.stats_service import StatsService
from services.vacancy_service import VacancyService
import traceback

api_bp = Blueprint('api', __name__)

# Инициализация сервисов
search_service = SearchService()
stats_service = StatsService()
vacancy_service = VacancyService()

@api_bp.route('/health')
def health():
    """Проверка работоспособности API"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'message': 'Job Parser System API работает',
        'parsers': ['hh', 'superjob']
    })

@api_bp.route('/search', methods=['POST'])
def search_vacancies():
    """Поиск вакансий на всех платформах"""
    try:
        data = request.json
        query = data.get('vacancy', '').strip()
        city = data.get('city', '')

        if not query:
            return jsonify({'error': 'Не указано название вакансии'}), 400

        results = search_service.search_all_sources(query, city)
        return jsonify(results)

    except Exception as e:
        print('💥 Ошибка в search_vacancies:', traceback.format_exc())
        return jsonify({'error': f'Ошибка на сервере: {str(e)}'}), 500

@api_bp.route('/vacancies', methods=['GET'])
def get_all_vacancies():
    """Получение всех вакансий из базы данных"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        source = request.args.get('source', '')
        company = request.args.get('company', '')

        result = vacancy_service.get_vacancies_paginated(
            page=page,
            per_page=per_page,
            source=source,
            company=company
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/clear-db', methods=['DELETE'])
def clear_database():
    """Полная очистка базы данных вакансий"""
    try:
        result = vacancy_service.clear_all_vacancies()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Ошибка очистки базы данных: {str(e)}'}), 500

@api_bp.route('/db-stats', methods=['GET'])
def get_db_stats():
    """Получение статистики базы данных"""
    try:
        stats = stats_service.get_db_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_full_stats():
    """Получение полной статистики"""
    try:
        stats = stats_service.get_full_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500