from flask import Blueprint, Response, session, redirect, url_for, flash
from services.export_service import ExportService

export_bp = Blueprint('export', __name__, url_prefix='/export')


def check_auth():
    """Проверка авторизации"""
    return 'user' in session


@export_bp.route('/csv')
def export_csv():
    """Экспорт в CSV"""
    if not check_auth():
        flash('Необходима авторизация для экспорта данных', 'warning')
        return redirect(url_for('auth.login_page'))

    try:
        export_service = ExportService()
        csv_data = export_service.export_to_csv()

        return Response(
            csv_data,
            mimetype='text/csv; charset=utf-8',
            headers={
                'Content-Disposition': 'attachment; filename=vacancies.csv',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
    except Exception as e:
        flash(f'Ошибка экспорта в CSV: {str(e)}', 'error')
        return redirect(url_for('main.index'))


@export_bp.route('/text')
def export_text():
    """Экспорт в текст"""
    if not check_auth():
        flash('Необходима авторизация для экспорта данных', 'warning')
        return redirect(url_for('auth.login_page'))

    try:
        export_service = ExportService()
        text_data = export_service.export_to_text()

        return Response(
            text_data,
            mimetype='text/plain; charset=utf-8',
            headers={
                'Content-Disposition': 'attachment; filename=vacancies.txt',
                'Content-Type': 'text/plain; charset=utf-8'
            }
        )
    except Exception as e:
        flash(f'Ошибка экспорта в текст: {str(e)}', 'error')
        return redirect(url_for('main.index'))