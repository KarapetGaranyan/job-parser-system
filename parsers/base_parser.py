from abc import ABC, abstractmethod
from typing import List, Dict


class BaseParser(ABC):
    """Базовый класс для всех парсеров"""

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def search(self, query: str, limit: int = 20, city: str = '') -> List[Dict]:
        """Поиск вакансий по запросу"""
        pass

    def save_vacancy(self, vacancy_data: Dict) -> bool:
        """Сохранение вакансии в базу данных"""
        try:
            from database.models import Vacancy, Session

            session = Session()
            try:
                # Проверяем, существует ли уже такая вакансия
                existing = session.query(Vacancy).filter_by(
                    link=vacancy_data['link']
                ).first()

                if existing:
                    return False  # Вакансия уже существует

                vacancy = Vacancy(
                    title=vacancy_data['title'],
                    link=vacancy_data['link'],
                    company=vacancy_data.get('company', ''),
                    salary=vacancy_data.get('salary', 'Не указана'),
                    source=self.source_name
                )

                session.add(vacancy)
                session.commit()
                return True

            except Exception as e:
                session.rollback()
                print(f"Ошибка сохранения вакансии: {e}")
                return False
            finally:
                session.close()

        except ImportError:
            # Если модели БД недоступны (например, в тестах), просто возвращаем True
            print(f"База данных недоступна, пропускаем сохранение: {vacancy_data['title']}")
            return True