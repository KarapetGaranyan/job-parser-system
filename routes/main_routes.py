# routes/main_routes.py - Добавляем обработку поиска
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from services.search_service import SearchService

main_bp = Blueprint('main', __name__)


def require_auth():
    """Простая проверка авторизации"""
    if 'user' not in session:
        flash('Необходима авторизация для доступа к системе', 'warning')
        return redirect(url_for('auth.login_page'))
    return None


@main_bp.route('/')
def index():
    """Главная страница с формой поиска"""
    auth_redirect = require_auth()
    if auth_redirect:
        return auth_redirect
    return render_template('index.html')


@main_bp.route('/search', methods=['POST'])
def search_vacancies():
    """Обработка поиска вакансий"""
    auth_redirect = require_auth()
    if auth_redirect:
        return auth_redirect

    try:
        # Получаем данные из формы
        query = request.form.get('query', '').strip()
        city = request.form.get('city', '').strip()

        if not query:
            flash('Введите название вакансии для поиска', 'warning')
            return redirect(url_for('main.index'))

        # Выполняем поиск
        search_service = SearchService()
        results = search_service.search_all_sources(query=query, city=city, limit=50)

        # Показываем результаты
        flash(f'Найдено {results["total"]} вакансий по запросу "{query}"', 'success')
        return render_template('search_results.html', results=results, query=query, city=city)

    except Exception as e:
        flash(f'Ошибка поиска: {str(e)}', 'error')
        return redirect(url_for('main.index'))


@main_bp.route('/vacancies')
def vacancies_page():
    """Страница всех вакансий"""
    auth_redirect = require_auth()
    if auth_redirect:
        return auth_redirect
    return render_template('vacancies.html')


@main_bp.route('/stats')
def stats_page():
    """Страница статистики"""
    auth_redirect = require_auth()
    if auth_redirect:
        return auth_redirect
    return render_template('stats.html')


@main_bp.route('/scheduler')
def scheduler_page():
    """Страница управления планировщиком"""
    auth_redirect = require_auth()
    if auth_redirect:
        return auth_redirect
    return render_template('scheduler.html')