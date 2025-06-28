from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Главная страница с формой поиска"""
    return render_template('index.html')

@main_bp.route('/vacancies')
def vacancies_page():
    """Страница всех вакансий"""
    return render_template('vacancies.html')

@main_bp.route('/stats')
def stats_page():
    """Страница статистики"""
    return render_template('stats.html')

@main_bp.route('/scheduler')
def scheduler_page():
    """Страница управления планировщиком"""
    return render_template('scheduler.html')