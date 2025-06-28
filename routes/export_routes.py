from flask import Blueprint, Response
from services.export_service import ExportService

export_bp = Blueprint('export', __name__)
export_service = ExportService()

@export_bp.route('/csv')
def export_csv():
    """Экспорт всех вакансий в CSV"""
    try:
        csv_data = export_service.export_to_csv()
        return Response(
            csv_data,
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment;filename=vacancies.csv'}
        )
    except Exception as e:
        return f'<pre>Ошибка экспорта: {str(e)}</pre>'

@export_bp.route('/text')
def export_text():
    """Текстовое представление всех вакансий"""
    try:
        text_data = export_service.export_to_text()
        return f'<pre style="font-family: monospace; white-space: pre-wrap; padding: 20px;">{text_data}</pre>'
    except Exception as e:
        return f'<pre>Ошибка: {str(e)}</pre>'