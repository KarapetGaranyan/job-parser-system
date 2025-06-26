import csv
import io
from typing import List
from database.models import Vacancy


class ExportUtils:
    """Утилиты для экспорта данных"""

    @staticmethod
    def to_csv(vacancies: List[Vacancy]) -> str:
        """Экспорт вакансий в CSV формат"""
        output = io.StringIO()

        # BOM для корректного отображения в Excel
        output.write('\ufeff')

        writer = csv.writer(output, delimiter=';')
        writer.writerow([
            'ID', 'Название', 'Компания', 'Зарплата',
            'Источник', 'Ссылка', 'Дата добавления'
        ])

        for vacancy in vacancies:
            writer.writerow([
                vacancy.id,
                vacancy.title,
                vacancy.company,
                vacancy.salary,
                vacancy.source,
                vacancy.link,
                vacancy.created_at.strftime('%Y-%m-%d %H:%M') if vacancy.created_at else ''
            ])

        return output.getvalue()

    @staticmethod
    def to_text(vacancies: List[Vacancy]) -> str:
        """Экспорт вакансий в текстовый формат"""
        lines = []
        lines.append("=" * 80)
        lines.append("                    СПИСОК ВАКАНСИЙ")
        lines.append("=" * 80)
        lines.append("")

        for i, vacancy in enumerate(vacancies, 1):
            lines.append(f"{i}. {vacancy.title}")
            lines.append(f"   Компания: {vacancy.company}")
            lines.append(f"   Зарплата: {vacancy.salary}")
            lines.append(f"   Источник: {vacancy.source.upper()}")
            lines.append(f"   Ссылка: {vacancy.link}")
            if vacancy.created_at:
                lines.append(f"   Добавлено: {vacancy.created_at.strftime('%Y-%m-%d %H:%M')}")
            lines.append("-" * 60)
            lines.append("")

        lines.append(f"Всего вакансий: {len(vacancies)}")
        lines.append("=" * 80)

        return "\n".join(lines)